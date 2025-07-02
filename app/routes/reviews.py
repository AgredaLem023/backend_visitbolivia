import logging
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List

from ..models import ReviewsResponse, ReviewModel
from ..services.google_sheets import google_sheets_service

# Create logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["reviews"])


def calculate_review_stats(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate review statistics"""
    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "star_distribution": {str(i): 0 for i in range(1, 6)}
        }
    
    total_reviews = len(reviews)
    total_rating = sum(review['rating'] for review in reviews)
    average_rating = round(total_rating / total_reviews, 1)
    
    # Calculate star distribution
    star_distribution = {str(i): 0 for i in range(1, 6)}
    for review in reviews:
        star_key = str(review['rating'])
        if star_key in star_distribution:
            star_distribution[star_key] += 1
    
    return {
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "star_distribution": star_distribution
    }


@router.get("/reviews/{package_id}", response_model=ReviewsResponse)
async def get_reviews(
    package_id: str = Path(..., description="Trip package ID (e.g., '4days', '11days')")
) -> ReviewsResponse:
    """
    Get reviews for a specific trip package
    
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
        
        # Get reviews from Google Sheets
        reviews_data = google_sheets_service.get_reviews_by_package(package_id)
        
        # Convert to ReviewModel objects
        reviews = []
        for review_dict in reviews_data:
            try:
                review = ReviewModel(**review_dict)
                reviews.append(review)
            except Exception as e:
                logger.warning(f"Skipping invalid review: {e}")
                continue
        
        # Calculate statistics
        stats = calculate_review_stats(reviews_data)
        
        # Return response
        return ReviewsResponse(
            reviews=reviews,
            total_reviews=stats["total_reviews"],
            average_rating=stats["average_rating"],
            star_distribution=stats["star_distribution"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_reviews endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/reviews/{package_id}/stats")
async def get_review_stats(
    package_id: str = Path(..., description="Trip package ID")
) -> Dict[str, Any]:
    """Get only the review statistics for a package"""
    try:
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        reviews_data = google_sheets_service.get_reviews_by_package(package_id)
        stats = calculate_review_stats(reviews_data)
        
        return {
            "package_id": package_id,
            **stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 