from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

app = FastAPI(
    title="Mock Numin API",
    description="Mock API for testing Numin predictions in QuantConnect",
    version="1.0.0"
)

# Enable CORS for QuantConnect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class PredictionRequest(BaseModel):
    ticker: str = "SPY"
    timeframe: str = "daily"
    start_date: str = "2024-10-28"

# Response model
class PredictionResponse(BaseModel):
    ticker: str
    timeframe: str
    startDate: str
    clusteredProjection: Dict[str, float]
    consolidatedProjection: Dict[str, float]

# Mock prediction data
MOCK_DATA = {
    "ticker": "SPY",
    "timeframe": "daily",
    "startDate": "2024-10-28",
    "clusteredProjection": {
        "2024-10-29": 573.2,
        "2024-10-30": 565.99,
        "2024-10-31": 572.23,
        "2024-11-01": 565.03,
        "2024-11-04": 565.2,
        "2024-11-05": 570.33,
        "2024-11-06": 589.16,
        "2024-11-07": 591.17,
        "2024-11-08": 582.72,
        "2024-11-11": 551.06,
        "2024-11-12": 586.33,
        "2024-11-13": 594.17,
        "2024-11-14": 595.54,
    },
    "consolidatedProjection": {
        "2024-10-29": 573.6,
        "2024-10-30": 565.92,
        "2024-10-31": 574.18,
        "2024-11-01": 567.11,
        "2024-11-04": 571.32,
        "2024-11-05": 578.48,
        "2024-11-06": 584.61,
        "2024-11-07": 583.94,
        "2024-11-08": 584.55,
        "2024-11-11": 565.16,
        "2024-11-12": 589.03,
        "2024-11-13": 591.67,
        "2024-11-14": 591.31,
    }
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mock Numin API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mock Numin API",
        "version": "1.0.0"
    }

@app.post("/projection/single-ticker", response_model=PredictionResponse)
async def get_predictions(request: PredictionRequest):
    """
    Get price predictions for a single ticker
    
    Matches real Numin API structure
    """
    try:
        # In production, this would query your database/model
        response = MOCK_DATA.copy()
        response["ticker"] = request.ticker
        response["timeframe"] = request.timeframe
        response["startDate"] = request.start_date
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")

@app.get("/projection/single-ticker")
async def get_predictions_get(
    ticker: str = "SPY",
    timeframe: str = "daily",
    start_date: str = "2024-10-28"
):
    """
    GET version of predictions endpoint (for easy browser testing)
    """
    request = PredictionRequest(
        ticker=ticker,
        timeframe=timeframe,
        start_date=start_date
    )
    return await get_predictions(request)

if __name__ == "__main__":
    uvicorn.run(
        "mock_numin_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )