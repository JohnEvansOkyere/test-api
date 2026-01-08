from AlgorithmImports import *
import json
from datetime import datetime

class NuminAPITradingAlgorithm(QCAlgorithm):
    def Initialize(self):
        # Set backtest period
        self.SetStartDate(2024, 10, 28)
        self.SetEndDate(2024, 11, 15)
        self.SetCash(100000)
        
        # Add SPY equity
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # Setup chart
        self.AddChart(Chart("Predictions vs Actual"))
        self.AddSeries("Predictions vs Actual", "Actual Price", SeriesType.Line)
        self.AddSeries("Predictions vs Actual", "Clustered Prediction", SeriesType.Line)
        
        # API Configuration - BASE URL ONLY
        self.api_base_url = "https://test-api-17u2.onrender.com"
        
        # Initialize prediction storage
        self.clustered = {}
        self.consolidated = {}
        
        # Load predictions from API
        self.LoadPredictionsFromAPI()
        
        # Trading parameters
        self.threshold = 0.01
        self.use_clustered = True
        
        # Debug: Show what was loaded
        if self.clustered:
            first_3 = list(self.clustered.keys())[:3]
            self.Debug(f"[API] First 3 prediction dates: {first_3}")
    
    def LoadPredictionsFromAPI(self):
        """Load predictions from FastAPI using GET request"""
        try:
            # Build URL with query parameters (GET request)
            url = f"{self.api_base_url}/projection/single-ticker?ticker=SPY&timeframe=daily&start_date=2024-10-28"
            
            self.Debug(f"[API] Calling: {url}")
            
            # Simple GET request - just pass URL
            response = self.Download(url)
            
            # Check if response is valid
            if not response or len(response) == 0:
                self.Error("[API] Empty response from API")
                return
            
            self.Debug(f"[API] Response received (length: {len(response)})")
            
            # Parse JSON response
            data = json.loads(response)
            
            # Verify response structure
            if "clusteredProjection" not in data:
                self.Error("[API] Missing 'clusteredProjection' in response")
                self.Debug(f"[API] Response keys: {list(data.keys())}")
                return
            
            # Convert string dates to date objects
            self.clustered = self.ParseDates(data.get("clusteredProjection", {}))
            self.consolidated = self.ParseDates(data.get("consolidatedProjection", {}))
            
            self.Debug(
                f"[API] Successfully loaded {len(self.clustered)} clustered & "
                f"{len(self.consolidated)} consolidated predictions"
            )
            
        except json.JSONDecodeError as e:
            self.Error(f"[API] JSON decode error: {str(e)}")
            self.Debug(f"[API] Response preview: {response[:200] if response else 'None'}")
        except Exception as e:
            self.Error(f"[API] Error: {str(e)}")
            import traceback
            self.Debug(f"[API] Traceback: {traceback.format_exc()}")
    
    def ParseDates(self, projection):
        """Convert string dates to date objects"""
        parsed = {}
        try:
            for date_str, value in projection.items():
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                parsed[date_obj] = float(value)
        except Exception as e:
            self.Error(f"[ParseDates] Error: {str(e)}")
        return parsed
    
    def OnData(self, data):
        """Main trading logic"""
        if not data.ContainsKey(self.symbol):
            return
        
        today = self.Time.date()
        current_price = self.Securities[self.symbol].Price
        
        # Plot actual price
        self.Plot("Predictions vs Actual", "Actual Price", current_price)
        
        # Plot BOTH predictions
        if today in self.clustered:
            self.Plot("Predictions vs Actual", "Clustered Prediction", self.clustered[today])
        
        if today in self.consolidated:
            self.Plot("Predictions vs Actual", "Consolidated Prediction", self.consolidated[today])
        
        # Get predictions for trading (uses clustered or consolidated based on setting)
        predictions = self.clustered if self.use_clustered else self.consolidated
        
        # Check for prediction
        if today in predictions:
            predicted_price = predictions[today]
            
            # Calculate expected return
            expected_return = (predicted_price - current_price) / current_price
            
            # Trading logic
            if expected_return > self.threshold:
                if not self.Portfolio[self.symbol].Invested:
                    self.SetHoldings(self.symbol, 1.0)
                    self.Debug(
                        f"[TRADE] BUY - Current: ${current_price:.2f}, "
                        f"Predicted: ${predicted_price:.2f}, "
                        f"Expected: {expected_return:.2%}"
                    )
            
            elif expected_return < -self.threshold:
                if self.Portfolio[self.symbol].Invested:
                    self.Liquidate(self.symbol)
                    self.Debug(
                        f"[TRADE] SELL - Current: ${current_price:.2f}, "
                        f"Predicted: ${predicted_price:.2f}, "
                        f"Expected: {expected_return:.2%}"
                    )
    
    def OnEndOfAlgorithm(self):
        """Summary statistics"""
        self.Debug(f"\n{'='*50}")
        self.Debug(f"BACKTEST SUMMARY")
        self.Debug(f"{'='*50}")
        self.Debug(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.2f}")
        self.Debug(f"Total Return: {((self.Portfolio.TotalPortfolioValue / 100000) - 1) * 100:.2f}%")
        self.Debug(f"{'='*50}\n")