# HealthCheck Dashboard API

Backend API for the HealthCheck Dashboard system providing store and user data management.

## Features

- RESTful API with proper authentication
- Store and user data management
- Data filtering, sorting, and pagination
- Excel export functionality
- Comprehensive logging
- Docker support

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/session/validate` - Validate session

### Data
- `GET /api/data/store-data` - Get store data
- `GET /api/data/user-data` - Get user data
- `GET /api/data/filters/unique` - Get filter options
- `GET /api/data/filters/user-roles` - Get user roles
- `GET /api/data/stats/user-count` - Get user statistics

### Export
- `POST /api/export/store-data` - Export store data to Excel
- `POST /api/export/user-data` - Export user data to Excel

### System
- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/refresh-all` - Refresh data caches

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

## run
- uvicorn app.main:app --reload
