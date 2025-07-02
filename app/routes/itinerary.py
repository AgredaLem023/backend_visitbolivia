from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List

from ..services.google_sheets import google_sheets_service
from ..models import ItineraryResponse, ItineraryDayModel

router = APIRouter(prefix="/api", tags=["itinerary"])


@router.get("/itinerary/{package_id}", response_model=ItineraryResponse)
async def get_itinerary(
    package_id: str = Path(..., description="Trip package ID (e.g., '4days', '11days')")
) -> ItineraryResponse:
    """
    Get itinerary data for a specific trip package
    
    Package IDs:
    - 4days: 4-day trip package
    - 11days: 11-day trip package
    - 15days: 15-day trip package
    - 25days: 25-day trip package
    """
    try:
        # Validate package ID
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        # Get itinerary data from Google Sheets
        itinerary_data = google_sheets_service.get_itinerary_by_package(package_id)
        
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
        print(f"❌ Error in get_itinerary endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/itinerary/{package_id}/day/{day_number}")
async def get_itinerary_day(
    package_id: str = Path(..., description="Trip package ID"),
    day_number: int = Path(..., description="Day number (1-based)")
) -> Dict[str, Any]:
    """Get itinerary data for a specific day of a specific package"""
    try:
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        if day_number < 1:
            raise HTTPException(
                status_code=400,
                detail="Day number must be 1 or greater"
            )
        
        # Get all itinerary data then filter for specific day
        all_itinerary = google_sheets_service.get_itinerary_by_package(package_id)
        
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
            "day_data": day_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 