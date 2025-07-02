import os
import json
from typing import List, Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google Sheets Configuration - JSON credentials instead of file path
    google_credentials_json: str = ""
    
    # Spreadsheet IDs for each trip package
    google_sheets_4days_id: str = ""
    google_sheets_11days_id: str = ""
    google_sheets_15days_id: str = ""
    google_sheets_25days_id: str = ""
    
    # Worksheet names (consistent across all spreadsheets)
    reviews_worksheet_name: str = "reviews_data"
    images_worksheet_name: str = "images_data"
    itinerary_worksheet_name: str = "itinerary_data"
    
    # API Configuration - Dynamic PORT for cloud deployment
    api_host: str = "0.0.0.0"
    api_port: int = int(os.environ.get("PORT", 8000))  # Render provides PORT env var
    api_reload: bool = True
    
    # CORS Configuration
    frontend_4days_url: str = "https://4-dias.visitbolivia.travel" #
    frontend_4days_url_2: str = "https://prueba-paquete.visitbolivia.travel"
    frontend_11days_url: str = "https://11-dias.visitbolivia.travel"
    frontend_15days_url: str = "https://15-dias.visitbolivia.travel"
    frontend_25days_url: str = "https://25-dias.visitbolivia.travel"
    local_frontend_url: str = "http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get list of allowed CORS origins"""
        origins = [
            self.frontend_4days_url,
            self.frontend_4days_url_2,
            self.frontend_11days_url,
            self.frontend_15days_url,
            self.frontend_25days_url,
            self.local_frontend_url,
        ]
        
        # Add localhost variations for development only
        if self.environment == "development":
            origins.extend([
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://localhost:3002",
                "http://localhost:3003",
                "http://127.0.0.1:3000"
            ])
        
        return origins
    
    def get_spreadsheet_id(self, package_id: str) -> str:
        """Get the spreadsheet ID for a specific package"""
        spreadsheet_mapping = {
            "4days": self.google_sheets_4days_id,
            "11days": self.google_sheets_11days_id,
            "15days": self.google_sheets_15days_id,
            "25days": self.google_sheets_25days_id,
        }
        return spreadsheet_mapping.get(package_id, "")
    
    def get_google_credentials_dict(self) -> Dict:
        """Parse Google credentials JSON string and return as dictionary"""
        try:
            if not self.google_credentials_json:
                raise ValueError("Google credentials JSON not provided")
            
            # Parse JSON string to dictionary
            credentials_dict = json.loads(self.google_credentials_json)
            return credentials_dict
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in google_credentials_json: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing Google credentials: {str(e)}")

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings() 