"""
Visit Bolivia Backend - Data Models
===================================

Author: Sergio Agreda (sergioagreda21@outlook.com)
GitHub: @AgredaLem023
Project: Visit Bolivia - Travel Package Management Backend

Copyright © [YEAR] Sergio Agreda. All rights reserved.
This code is proprietary and confidential.

Originally developed by Sergio Agreda for Visit Bolivia business operations.

Description:
Pydantic data models for API request/response validation including reviews,
images, itinerary, and health check models for the travel package system.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ReviewModel(BaseModel):
    """Model for a single review"""
    id: int
    name: str
    date: str
    rating: int
    body: str


class ReviewsResponse(BaseModel):
    """Response model for reviews endpoint"""
    reviews: List[ReviewModel]
    total_reviews: int
    average_rating: float
    star_distribution: dict


class ImageModel(BaseModel):
    """Model for a single image"""
    id: int
    url: str
    category: str
    alt_text: str
    alt_text_en: str


class ImagesResponse(BaseModel):
    """Response model for images endpoint"""
    package_id: str
    images: List[ImageModel]
    total_images: int


class TripPackageInfo(BaseModel):
    """Basic trip package information"""
    package_id: str
    name: str
    days: int
    description: Optional[str] = None


class ItineraryDayModel(BaseModel):
    """Model for a single day in the itinerary"""
    day: int
    title: str
    description: str
    accommodation: str
    included_activities: str
    meals: str
    optional_activities: List[str]
    special_info: str


class ItineraryResponse(BaseModel):
    """Response model for itinerary endpoint"""
    package_id: str
    itinerary: List[ItineraryDayModel]
    total_days: int


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: datetime 