# Visit Bolivia - Trip Packages Backend API

FastAPI backend service for managing trip package data and reviews via Google Sheets integration.

## Authorship & Development

**Original Developer:** Sergio Agreda  
**Email:** sergioagreda21@outlook.com  
**GitHub:** [@AgredaLem023](https://github.com/AgredaLem023)  
**Development Period:** [SPECIFY DATES]  
**Project:** Visit Bolivia - Travel Package Management Backend  

> **Copyright © 2025 Sergio Agreda. All rights reserved.**  
> This code is proprietary and confidential.  
> Originally developed by Sergio Agreda for Visit Bolivia business operations.  
> Transferred from personal to business accounts while maintaining authorship.

### Technology Stack
- **Framework:** FastAPI (Python)
- **Data Integration:** Google Sheets API
- **Validation:** Pydantic models
- **Authentication:** Google Service Account
- **Deployment:** Cloud-ready (Render/Heroku)
- **Architecture:** RESTful API with microservices pattern

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (already created as `venv_visit`)
- Google Service Account JSON file

### Installation

1. **Activate virtual environment:**
   ```bash
   .\venv_visit\Scripts\activate  # Windows
   source venv_visit/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   - Copy `env_template.txt` to `.env`
   - Update values with your configuration

4. **Add Google Service Account:**
   - Create `credentials/` folder
   - Place your service account JSON file in `credentials/service-account-key.json`

### Running the API

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check with Google Sheets connection status

### Reviews
- `GET /api/reviews/{package_id}` - Get all reviews for a trip package
- `GET /api/reviews/{package_id}/stats` - Get review statistics only

### Package IDs
- `4days` - 4-day trip package
- `11days` - 11-day trip package  
- `15days` - 15-day trip package
- `25days` - 25-day trip package

## Google Sheets Structure

Expected sheet format (`Reviews` sheet):

| Column A | Column B | Column C | Column D | Column E |
|----------|----------|----------|----------|----------|
| Package ID | Reviewer Name | Review Date | Rating (1-5) | Review Text |
| 4days | John Doe | December 2024 | 5 | Amazing trip! |
| 11days | Jane Smith | November 2024 | 4 | Great experience |

## Configuration

Environment variables (see `env_template.txt`):

- `GOOGLE_SHEETS_CREDENTIALS_PATH` - Path to service account JSON
- `GOOGLE_SHEETS_SPREADSHEET_ID` - Your Google Sheets ID
- `API_HOST` / `API_PORT` - Server configuration
- Frontend URLs for CORS

## Frontend Integration

The API is configured to accept requests from:
- Local development: `http://localhost:3000`
- Production subdomains: `https://{4,11,15,25}dias.visitbolivia.travel`

## Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Get reviews for 4-day package
curl http://localhost:8000/api/reviews/4days
``` 

## Backend Structure
```bash
backend_trip_packages/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application (209 lines)
│   ├── config.py            # Configuration & settings (94 lines)
│   ├── models.py            # Pydantic data models (70 lines)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── reviews.py       # Review API endpoints (124 lines)
│   │   ├── images.py        # Image API endpoints (154 lines)
│   │   └── itinerary.py     # Itinerary API endpoints (139 lines)
│   └── services/
│       ├── __init__.py
│       └── google_sheets.py # Google Sheets integration (269 lines)
├── requirements.txt         # Dependencies (57 packages)
├── env_template.txt        # Environment variables template
├── README.md               # Complete documentation
├── AUTHORS.md              # Development history & authorship
├── LICENSE                 # Proprietary license
├── Procfile                # Deployment configuration
├── runtime.txt             # Python version specification
└── venv_visit/            # Virtual environment
```

## Features & Capabilities

### Core Functionality
- **Multi-Package Support:** 4, 11, 15, and 25-day Bolivia trip packages
- **Review Management:** Customer feedback with ratings and statistics
- **Image Management:** Photo galleries with category-based organization
- **Itinerary Management:** Day-by-day trip planning with multi-language support
- **Health Monitoring:** Comprehensive health checks and system status

### Advanced Features
- **Multi-language Support:** Spanish and English content management
- **Google Sheets Integration:** Database-less architecture with real-time data
- **Image Proxying:** Optimized image delivery and URL conversion
- **CORS Configuration:** Secure frontend integration
- **Error Handling:** Robust error management and logging
- **Cloud Deployment:** Production-ready configuration

## Development Architecture

### Design Principles
- **Modular Architecture:** Separation of concerns with clear service boundaries
- **Type Safety:** Comprehensive type hints and Pydantic validation
- **Error Handling:** Structured error responses and logging
- **Performance:** Efficient Google Sheets API integration
- **Security:** Secure authentication and CORS configuration

### Code Quality
- **Total Lines:** ~1,000+ lines of production-ready Python code
- **Documentation:** Comprehensive code comments and API documentation
- **Testing:** Health check endpoints and error handling
- **Deployment:** Cloud-ready with environment configuration

## License & Copyright

This project is proprietary software developed by Sergio Agreda for Visit Bolivia.

**Copyright © [YEAR] Sergio Agreda (sergioagreda21@outlook.com)**  
All rights reserved.

See `LICENSE` file for complete terms and conditions.
See `AUTHORS.md` for detailed development history and contributions.

## Contact & Support

For questions regarding this backend system or development:

**Developer:** Sergio Agreda  
**Email:** sergioagreda21@outlook.com  
**GitHub:** [@AgredaLem023](https://github.com/AgredaLem023)  
**Project:** Visit Bolivia - Travel Package Management System  

---

*This backend system was originally developed by Sergio Agreda and transferred to Visit Bolivia business operations while maintaining original authorship and intellectual property rights.*