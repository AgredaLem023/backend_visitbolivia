import logging
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import Response
import httpx
from typing import Dict, Any, List

from ..models import ImagesResponse, ImageModel
from ..services.google_sheets import google_sheets_service

# Create logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["images"])


@router.get("/images/{package_id}", response_model=ImagesResponse)
async def get_images(
    package_id: str = Path(..., description="Trip package ID (e.g., '4days', '11days')")
) -> ImagesResponse:
    """
    Get images for a specific trip package
    
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
        
        # Get images from Google Sheets
        images_data = google_sheets_service.get_images_by_package(package_id)
        
        # Convert to ImageModel objects
        images = []
        for image_dict in images_data:
            try:
                image = ImageModel(**image_dict)
                images.append(image)
            except Exception as e:
                logger.warning(f"Skipping invalid image: {e}")
                continue
        
        return ImagesResponse(
            package_id=package_id,
            images=images,
            total_images=len(images)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_images endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/images/{package_id}/proxy/{image_id}")
async def proxy_image(
    package_id: str = Path(..., description="Trip package ID"),
    image_id: int = Path(..., description="Image ID")
):
    """Proxy endpoint to serve images and avoid CORS issues"""
    try:
        # Get images data
        images_data = google_sheets_service.get_images_by_package(package_id)
        
        # Find the specific image
        target_image = None
        for img in images_data:
            if img.get('id') == image_id:
                target_image = img
                break
        
        if not target_image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Fetch the image from Google Drive
        async with httpx.AsyncClient() as client:
            response = await client.get(target_image['url'])
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Image not accessible")
            
            # Return the image with proper headers
            return Response(
                content=response.content,
                media_type=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                    "Access-Control-Allow-Origin": "*"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error proxying image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to proxy image")


@router.get("/images/{package_id}/category/{category}")
async def get_images_by_category(
    package_id: str = Path(..., description="Trip package ID"),
    category: str = Path(..., description="Image category (e.g., 'overview', 'itinerary', 'hero')")
) -> Dict[str, Any]:
    """Get images filtered by category for a specific package"""
    try:
        valid_packages = ["4days", "11days", "15days", "25days"]
        if package_id not in valid_packages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package_id. Must be one of: {', '.join(valid_packages)}"
            )
        
        # Get all images then filter by category
        all_images_data = google_sheets_service.get_images_by_package(package_id)
        filtered_images_data = [
            img for img in all_images_data 
            if img.get('category', '').lower() == category.lower()
        ]
        
        # Convert to ImageModel objects
        filtered_images = []
        for image_dict in filtered_images_data:
            try:
                image = ImageModel(**image_dict)
                filtered_images.append(image)
            except Exception as e:
                logger.warning(f"Skipping invalid image: {e}")
                continue
        
        return {
            "package_id": package_id,
            "category": category,
            "images": filtered_images,
            "total_images": len(filtered_images)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 