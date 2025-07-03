import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .config import settings
from .models import HealthCheck
from .routes import reviews, images, itinerary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger for main module
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Visit Bolivia - Trip Packages API",
    description="Backend API for managing trip package data and reviews via Google Sheets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.visitbolivia\.travel",
)

# Include routers
app.include_router(reviews.router)
app.include_router(images.router)
app.include_router(itinerary.router)


@app.get("/", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        message="Visit Bolivia Trip Packages API is running",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck)
async def detailed_health_check():
    """Detailed health check with system information"""
    try:
        # Test Google Sheets connection
        from .services.google_sheets import google_sheets_service
        
        # This will validate credentials exist
        google_sheets_service.authenticate()
        sheets_status = "connected"
        
    except Exception as e:
        sheets_status = f"error: {str(e)}"
    
    return HealthCheck(
        status="healthy" if "error" not in sheets_status else "degraded",
        message=f"API Status: OK | Google Sheets: {sheets_status}",
        timestamp=datetime.now()
    )


@app.get("/api/packages")
async def get_available_packages():
    """Get list of available trip packages"""
    return {
        "packages": [
            {
                "id": "4days",
                "name": "4-Day Bolivia Adventure",
                "description": "Short but intense adventure through Bolivia's highlights",
                "endpoints": {
                    "reviews": "/api/reviews/4days",
                    "images": "/api/images/4days", 
                    "itinerary": "/api/itinerary/4days"
                }
            },
            {
                "id": "11days",
                "name": "11-Day Bolivia Explorer",
                "description": "Extended exploration of Bolivia's diverse landscapes",
                "endpoints": {
                    "reviews": "/api/reviews/11days",
                    "images": "/api/images/11days",
                    "itinerary": "/api/itinerary/11days"
                }
            },
            {
                "id": "15days", 
                "name": "15-Day Bolivia Complete",
                "description": "Comprehensive tour covering all major attractions",
                "endpoints": {
                    "reviews": "/api/reviews/15days",
                    "images": "/api/images/15days",
                    "itinerary": "/api/itinerary/15days"
                }
            },
            {
                "id": "25days",
                "name": "25-Day Bolivia Ultimate",
                "description": "Ultimate Bolivia experience with in-depth exploration", 
                "endpoints": {
                    "reviews": "/api/reviews/25days",
                    "images": "/api/images/25days",
                    "itinerary": "/api/itinerary/25days"
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    ) 