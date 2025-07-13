"""
Visit Bolivia Backend - Itinerary API Routes
============================================

Author: Sergio Agreda (sergioagreda21@outlook.com)
GitHub: @AgredaLem023
Project: Visit Bolivia - Travel Package Management Backend

Copyright © [YEAR] Sergio Agreda. All rights reserved.
This code is proprietary and confidential.

Originally developed by Sergio Agreda for Visit Bolivia business operations.

Description:
FastAPI routes for managing travel package itineraries including day-by-day
schedules, activities, and multi-language support for Bolivia travel packages.
"""

import logging
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Any, List

from ..services.google_sheets import google_sheets_service
from ..models import ItineraryResponse, ItineraryDayModel

# Create logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["itinerary"])


@router.get("/itinerary/{package_id}", response_model=ItineraryResponse)
async def get_itinerary(
    package_id: str = Path(..., description="Trip package ID (e.g., '4days', '11days')"),
    lang: str = Query("es", description="Language code (es for Spanish, en for English)")
) -> ItineraryResponse:
    """
    Get itinerary data for a specific trip package in the specified language
    
    Package IDs:
    - 4days: 4-day trip package
    - 11days: 11-day trip package
    - 15days: 15-day trip package
    - 25days: 25-day trip package
    
    Languages:
    - es: Spanish (default) - fetches from 'itinerary_data' worksheet
    - en: English - fetches from 'itinerary_data_en' worksheet
    """
    try:
        # Validate package ID
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        # Validate language
        valid_languages = ["es", "en"]
        if lang not in valid_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(valid_languages)}"
            )
        
        # Get itinerary data from Google Sheets with language parameter
        itinerary_data = google_sheets_service.get_itinerary_by_package(package_id, lang)
        
        # Convert to Pydantic models
        itinerary_days = []
        for day_data in itinerary_data:
            itinerary_day = ItineraryDayModel(
                day=day_data.get('day', 1),
                title=day_data.get('title', ''),
                description=day_data.get('description', ''),
                accommodation=day_data.get('accommodation', ''),
                included_activities=day_data.get('included_activities', ''),
                meals=day_data.get('meals', ''),
                optional_activities=day_data.get('optional_activities', []),
                special_info=day_data.get('special_info', '')
            )
            itinerary_days.append(itinerary_day)
        
        return ItineraryResponse(
            package_id=package_id,
            itinerary=itinerary_days,
            total_days=len(itinerary_days)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_itinerary endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/itinerary/{package_id}/day/{day_number}")
async def get_itinerary_day(
    package_id: str = Path(..., description="Trip package ID"),
    day_number: int = Path(..., description="Day number (1-based)"),
    lang: str = Query("es", description="Language code (es for Spanish, en for English)")
) -> Dict[str, Any]:
    """Get itinerary data for a specific day of a specific package in the specified language"""
    try:
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        valid_languages = ["es", "en"]
        if lang not in valid_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(valid_languages)}"
            )
        
        if day_number < 1:
            raise HTTPException(
                status_code=400,
                detail="Day number must be 1 or greater"
            )
        
        # Get all itinerary data then filter for specific day
        all_itinerary = google_sheets_service.get_itinerary_by_package(package_id, lang)
        
        # Find the specific day
        day_data = None
        for day in all_itinerary:
            if day.get('day') == day_number:
                day_data = day
                break
        
        if not day_data:
            raise HTTPException(
                status_code=404,
                detail=f"Day {day_number} not found for package {package_id}"
            )
        
        return {
            "package_id": package_id,
            "day_data": day_data,
            "language": lang
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 