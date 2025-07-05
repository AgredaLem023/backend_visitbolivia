import logging
import sys
import os
import time
from fastapi import FastAPI, Request
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.visitbolivia\.travel",
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include routers
app.include_router(reviews.router)
app.include_router(images.router)
app.include_router(itinerary.router)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"Incoming {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Query params: {dict(request.query_params)}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response


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


@app.get("/health/detailed")
async def comprehensive_health_check():
    """Comprehensive health check for debugging production issues"""
    try:
        from .services.google_sheets import google_sheets_service
        
        # Test Google Sheets connection
        try:
            google_sheets_service.authenticate()
            sheets_status = "connected"
            
            # Test actual data retrieval
            test_reviews = google_sheets_service.get_reviews_by_package("4days")
            test_images = google_sheets_service.get_images_by_package("4days")
            test_itinerary = google_sheets_service.get_itinerary_by_package("4days", "es")
            
            services_test = {
                "reviews": len(test_reviews) if test_reviews else 0,
                "images": len(test_images) if test_images else 0,
                "itinerary": len(test_itinerary) if test_itinerary else 0
            }
        except Exception as e:
            sheets_status = f"error: {str(e)}"
            services_test = {"error": str(e)}
        
        # Test environment variables
        env_check = {
            "NODE_ENV": os.environ.get("NODE_ENV", "not_set"),
            "PORT": os.environ.get("PORT", "not_set"),
            "has_google_credentials": bool(settings.google_credentials_json),
            "has_spreadsheet_id": bool(settings.google_sheets_4days_id),
            "allowed_origins_count": len(settings.allowed_origins)
        }
        
        return {
            "status": "healthy" if "error" not in sheets_status else "degraded",
            "timestamp": datetime.now(),
            "google_sheets": sheets_status,
            "services_test": services_test,
            "environment": env_check,
            "cors_origins": settings.allowed_origins
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now(),
            "error": str(e)
        }


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