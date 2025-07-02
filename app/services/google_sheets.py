import os
import json
import re
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings
from ..models import ReviewModel


def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive sharing URL to direct image URL"""
    if not url or 'drive.google.com' not in url:
        return url
    
    # Extract file ID from Google Drive URL
    # Patterns: 
    # https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    # https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
    pattern = r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    
    if match:
        file_id = match.group(1)
        # Convert to direct image URL using usercontent domain (no redirects)
        direct_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=view&authuser=0"
        print(f"📸 Converted Drive URL: {url} -> {direct_url}")
        return direct_url
    
    print(f"⚠️ Could not convert Drive URL: {url}")
    return url


class GoogleSheetsService:
    """Service to interact with Google Sheets API"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API using service account"""
        try:
            # Define the scope
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            # Load credentials from service account file
            credentials_path = settings.google_sheets_credentials_path
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
            
            self.credentials = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("✅ Google Sheets authentication successful")
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {str(e)}")
            raise e
    
    def get_sheet_data(self, spreadsheet_id: str, worksheet_name: str, range_name: str = None) -> List[List[str]]:
        """Get data from a specific worksheet in a spreadsheet"""
        try:
            if not self.service:
                self.authenticate()
            
            # Build the range (worksheet_name!range or just worksheet_name for all data)
            full_range = f"{worksheet_name}!{range_name}" if range_name else worksheet_name
            
            # Call the Sheets API
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=full_range
            ).execute()
            
            values = result.get('values', [])
            print(f"✅ Retrieved {len(values)} rows from {worksheet_name}")
            return values
            
        except HttpError as error:
            print(f"❌ HTTP Error retrieving data from {worksheet_name}: {error}")
            raise error
        except Exception as error:
            print(f"❌ Error retrieving data from {worksheet_name}: {error}")
            raise error
    
    def get_reviews_by_package(self, package_id: str) -> List[Dict[str, Any]]:
        """Get reviews for a specific trip package"""
        try:
            # Get the spreadsheet ID for this package
            spreadsheet_id = settings.get_spreadsheet_id(package_id)
            if not spreadsheet_id:
                raise ValueError(f"No spreadsheet ID configured for package: {package_id}")
            
            # Get data from reviews worksheet
            worksheet_name = settings.reviews_worksheet_name  # "reviews_data"
            data = self.get_sheet_data(spreadsheet_id, worksheet_name)
            
            if not data:
                print(f"⚠️ No data found in {worksheet_name} for package {package_id}")
                return []
            
            # Skip header row and process data
            headers = data[0] if data else []
            rows = data[1:] if len(data) > 1 else []
            
            print(f"📊 Headers found: {headers}")
            print(f"📊 Processing {len(rows)} review rows")
            
            reviews = []
            for i, row in enumerate(rows, start=2):  # start=2 because row 1 is headers
                try:
                    # Ensure row has enough columns
                    while len(row) < 5:
                        row.append("")
                    
                    review = {
                        'name': row[0] if row[0] else f"Anonymous {i}",
                        'date': row[1] if row[1] else "2024-01-01",
                        'rating': int(row[2]) if row[2] and row[2].isdigit() else 5,
                        'body': row[3] if row[3] else "Great experience!",
                        'id': int(row[4]) if row[4] and row[4].isdigit() else i
                    }
                    reviews.append(review)
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Skipping row {i} due to error: {e}")
                    continue
            
            print(f"✅ Successfully processed {len(reviews)} reviews for {package_id}")
            return reviews
            
        except Exception as e:
            print(f"❌ Error getting reviews for {package_id}: {str(e)}")
            raise e
    
    def get_images_by_package(self, package_id: str) -> List[Dict[str, Any]]:
        """Get images for a specific trip package"""
        try:
            spreadsheet_id = settings.get_spreadsheet_id(package_id)
            if not spreadsheet_id:
                raise ValueError(f"No spreadsheet ID configured for package: {package_id}")
            
            worksheet_name = settings.images_worksheet_name  # "images_data"
            data = self.get_sheet_data(spreadsheet_id, worksheet_name)
            
            if not data or len(data) < 2:
                print(f"⚠️ No image data found in {worksheet_name} for package {package_id}")
                return []
            
            # Process images data (columns: id, url, category, alt_text)
            headers = data[0] if data else []
            rows = data[1:] if len(data) > 1 else []
            
            print(f"📊 Image headers found: {headers}")
            print(f"📊 Processing {len(rows)} image rows")
            
            images = []
            for i, row in enumerate(rows, start=2):
                try:
                    # Ensure row has enough columns
                    while len(row) < 4:
                        row.append("")
                    
                    # Convert Google Drive URLs to direct image URLs
                    original_url = row[1] if row[1] else ""
                    converted_url = convert_google_drive_url(original_url)
                    
                    image = {
                        'id': int(row[0]) if row[0] and str(row[0]).isdigit() else i,
                        'url': converted_url,
                        'category': row[2] if row[2] else "general",
                        'alt_text': row[3] if row[3] else f"Image {i}"
                    }
                    
                    # Skip rows with empty URLs
                    if not image['url']:
                        print(f"⚠️ Skipping row {i} - empty URL")
                        continue
                        
                    images.append(image)
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Skipping image row {i} due to error: {e}")
                    continue
            
            print(f"✅ Successfully processed {len(images)} images for {package_id}")
            return images
            
        except Exception as e:
            print(f"❌ Error getting images for {package_id}: {str(e)}")
            raise e
    
    def get_itinerary_by_package(self, package_id: str) -> List[Dict[str, Any]]:
        """Get itinerary data for a specific trip package"""
        try:
            spreadsheet_id = settings.get_spreadsheet_id(package_id)
            if not spreadsheet_id:
                raise ValueError(f"No spreadsheet ID configured for package: {package_id}")
            
            worksheet_name = settings.itinerary_worksheet_name  # "itinerary_data"
            data = self.get_sheet_data(spreadsheet_id, worksheet_name)
            
            if not data or len(data) < 2:
                print(f"⚠️ No itinerary data found in {worksheet_name} for package {package_id}")
                return []
            
            # Process itinerary data 
            # Expected columns: day, title, description, accommodation, included_activities, meals, optional_activities, special_info
            headers = data[0] if data else []
            rows = data[1:] if len(data) > 1 else []
            
            print(f"📊 Itinerary headers found: {headers}")
            print(f"📊 Processing {len(rows)} itinerary day rows")
            
            itinerary_days = []
            for i, row in enumerate(rows, start=2):
                try:
                    # Ensure row has enough columns (8 columns expected)
                    while len(row) < 8:
                        row.append("")
                    
                    # Parse optional activities (expecting comma-separated values or empty)
                    optional_activities_str = row[6] if row[6] else ""
                    optional_activities = [activity.strip() for activity in optional_activities_str.split(",") if activity.strip()] if optional_activities_str else []
                    
                    itinerary_day = {
                        'day': int(row[0]) if row[0] and str(row[0]).isdigit() else i-1,
                        'title': row[1] if row[1] else f"Day {i-1}",
                        'description': row[2] if row[2] else "",
                        'accommodation': row[3] if row[3] else "",
                        'included_activities': row[4] if row[4] else "",
                        'meals': row[5] if row[5] else "",
                        'optional_activities': optional_activities,
                        'special_info': row[7] if row[7] else ""
                    }
                    
                    itinerary_days.append(itinerary_day)
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Skipping itinerary day row {i} due to error: {e}")
                    continue
            
            print(f"✅ Successfully processed {len(itinerary_days)} itinerary days for {package_id}")
            return itinerary_days
            
        except Exception as e:
            print(f"❌ Error getting itinerary for {package_id}: {str(e)}")
            raise e


# Global service instance
google_sheets_service = GoogleSheetsService() 