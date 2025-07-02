# Visit Bolivia - Trip Packages Backend API

FastAPI backend service for managing trip package data and reviews via Google Sheets integration.

## 🚀 Quick Start

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

## 📋 API Endpoints

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

## 📊 Google Sheets Structure

Expected sheet format (`Reviews` sheet):

| Column A | Column B | Column C | Column D | Column E |
|----------|----------|----------|----------|----------|
| Package ID | Reviewer Name | Review Date | Rating (1-5) | Review Text |
| 4days | John Doe | December 2024 | 5 | Amazing trip! |
| 11days | Jane Smith | November 2024 | 4 | Great experience |

## 🔧 Configuration

Environment variables (see `env_template.txt`):

- `GOOGLE_SHEETS_CREDENTIALS_PATH` - Path to service account JSON
- `GOOGLE_SHEETS_SPREADSHEET_ID` - Your Google Sheets ID
- `API_HOST` / `API_PORT` - Server configuration
- Frontend URLs for CORS

## 🌐 Frontend Integration

The API is configured to accept requests from:
- Local development: `http://localhost:3000`
- Production subdomains: `https://{4,11,15,25}-dias.visitbolivia.travel`

## 📚 Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔍 Testing

Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Get reviews for 4-day package
curl http://localhost:8000/api/reviews/4days
``` 

## Backend structure
```bash
backend_trip_packages/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration & settings
│   ├── models.py            # Pydantic data models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── reviews.py       # Review API endpoints
│   └── services/
│       ├── __init__.py
│       └── google_sheets.py # Google Sheets integration
├── requirements.txt         # Dependencies
├── env_template.txt        # Environment variables template
├── README.md               # Complete documentation
└── venv_visit/            # Your virtual environment
```