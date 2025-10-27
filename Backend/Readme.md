# Python FastAPI Audit Service

A robust, scalable audit logging service built with FastAPI and PostgreSQL, designed to track and manage system events across multiple functionalities with advanced features like data partitioning, archival, and real-time search capabilities.

## Overview

This service provides a complete audit trail solution, offering:

- **Event Logging**: Capture user actions, system events, and business transactions
- **Advanced Search**: Filter and search audit events with multiple criteria
- **Data Export**: Export audit data to Excel format
- **Automatic Archival**: Smart data management with automatic archival of old records
- **Real-time Monitoring**: Live access to recent audit events
- **Scalable Architecture**: PostgreSQL partitioning for performance optimization

## Architecture

### Database Schema
- **auditfunctionalities**: Master table for system functionalities
- **auditeventtypes**: Event types categorized by functionality
- **auditevents**: Main audit events table with time-based partitioning
- **AuditEvents_Archival**: Archived events older than 12 months

### Key Features
- **Time-based Partitioning**: Monthly partitions for optimal performance
- **Automatic Maintenance**: Scheduled archival and partition management
- **Connection Pooling**: Optimized database connections
- **Central Time Handling**: All timestamps stored and processed in CT

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- FastAPI
- SQLAlchemy with async support
- CSIQ API key

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Backend
cd audit-service
```

### 2. Environment Setup
Create a `.env` file in the root directory:

```env
# Database Configuration
PG_HOST={pg_url}
PG_PORT=5432
PG_DATABASE={pg_database}
PG_USER={pg_username}
PG_PASSWORD={pg_password}

# Connection Pool Settings
POOL_SIZE=5
POOL_MAX_OVERFLOW=10
POOL_RECYCLE=1800
POOL_TIMEOUT=30

# Logging 'DEBUG' for local, 'INFO' for production
LOG_LEVEL=DEBUG 

```

### 3. Database Setup
Execute the SQL schema creation script:

```sql
**create_tables.sql
```

This will create:
- All necessary tables with partitions
- Stored procedures and functions
- Indexes for optimal performance
- Sample data for testing

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize Database
```bash
python -c "from app.configurations.base import initialize_db_if_not_created; import asyncio; asyncio.run(initialize_db_if_not_created())"
```

## Running the Service

### Development Mode
```bash
uvicorn app.main:app --reload
```


The service will be available at: `{base_url}/pyaudit/docs`

## API Documentation

### Interactive Documentation
- **Swagger UI**: `/pyaudit/docs`
- **ReDoc**: `/pyaudit/redoc`
- **OpenAPI Schema**: `/pyaudit/openapi.json`

## API Key Authentication
```
All endpoints (except healthcheck) require API key authentication:

Example:

GET /pyaudit/api/audit-events/recent
Headers: 
  CSIQ-APIKEY: {api-key}
```
## Testing in Swagger UI:
```
1. Go to `{base_url}/pyaudit/docs`
2. Click "Authorize" button
3. Enter your API key: {api_key}
4. All requests will automatically include the API key
```

## API Endpoints

### Health Check
```http
GET /pyaudit/api/healthcheck
```
Verifies service status and database connectivity.

### Create Audit Event
```http
POST /pyaudit/api/audit-events/create
```
Creates a new audit event with the following payload:

Example:

```json
{
  "event_timestamp": "2025-09-25T10:30:00Z",
  "functionality": "Authenticate",
  "event_type": "Login",
  "store_id": 101,
  "company_id": 5001,
  "user": "jdoe",
  "message": "User logged in successfully",
  "status": "Success",
  "additional_data": {
    "ip": "192.168.1.10",
    "browser": "Chrome"
  }
}
```

### Get Recent Events
```http
GET /pyaudit/api/audit-events/recent
```
Retrieves the 500 most recent audit events.

### Search Events
```http
GET /pyaudit/api/audit-events/search
```
Advanced search with multiple filter criteria:

| Parameter       | Type     | Description                      |
|-----------------|----------|----------------------------------|
| from_date       | datetime | Start date for search            |
| to_date         | datetime | End date for search              |
| functionality   | string   | Filter by functionality name     |
| store_id        | integer  | Filter by store location         |
| company_id      | integer  | Filter by company                |
| user            | string   | Filter by username               |
| message_pattern | string   | Text search in message content   |
| page_number     | integer  | Pagination (default: 1)          |
| page_size       | integer  | Page size 1-5000 (default: 500)  |

### Export to Excel
```http
GET /pyaudit/api/audit-events/export
```
Exports search results or recent events to Excel format with optional parameters:
- `recent=true`: Export recent 500 events
- All search parameters supported

### Get Event Types by Functionality
```http
GET /pyaudit/api/audit-events/get-eventtypenames-by-functionalityname
```
Retrieves available event types for a given functionality.

## Database Configuration

### Connection Management
The service uses SQLAlchemy with async support and connection pooling:

```python
# Configuration in dbconfig.py
pool_size=5                   # Minimum connections
max_overflow=10               # Maximum overflow connections
pool_recycle=1800             # Recycle connections every 30 minutes
pool_timeout=30               # Connection timeout in seconds
pool_pre_ping=True            # Validate connections before use
```

### Environment Support
- **Local Development**: Uses environment variables
- **Production**: Uses environment variables

## Database Maintenance

### Automated Partition Management
The service includes automated partition management:

```sql
-- Create monthly partitions
SELECT ensure_auditevents_partitions();

-- Run maintenance (archive old data, drop old partitions)
CALL sp_auditevents_maintain();
```

### Recommended Cron Job
Set up a monthly cron job for database maintenance:

```bash
# Monthly maintenance
0 2 1 * * psql -d audit_db -c "CALL sp_auditevents_maintain();"
```

## Data Model

### AuditEvent Entity
```python
class AuditEvent(BASE):
    id: BigInteger (Primary Key)
    eventtimestamp: DateTime (Primary Key, Partition Key)
    functionalityid: Integer (Foreign Key)
    eventtypeid: Integer (Foreign Key)
    storelocationid: BigInteger
    companyid: BigInteger
    username: String(20)
    message: Text
    status: String(20) ['Success', 'Failed']
    additionaldata: JSON
```

### Supported Functionalities & Event Types
| Functionality    | Event Types                                                             |
|------------------|-------------------------------------------------------------------------|
| Authenticate     | Login, Logout, Sign up, Reset Password                                  |
| Price Management | Item updated, Item updates picked up by publisher,                      |
                     Item updates pushed to rabbit MQ, Item updates acknowledgement received |

## Security Features

- CORS enabled for cross-origin requests
- Secure database connection handling
- Input validation with Pydantic models
- SQL injection prevention via parameterized queries

## Performance Optimizations

- **Database Partitioning**: Monthly partitions for faster queries
- **Connection Pooling**: Efficient resource utilization
- **Indexed Columns**: Optimized search performance
- **Async Operations**: Non-blocking database operations
- **Pagination**: Efficient large dataset handling

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check connection parameters in `.env`
   - Ensure database and user exist

2. **Partition Creation Issues**
   - Run `SELECT ensure_auditevents_partitions();` manually
   - Check PostgreSQL user has CREATE TABLE privileges

3. **Performance Issues**
   - Monitor connection pool settings
   - Check partition maintenance is running
   - Verify indexes are being used

## Security
```
1. Global API Key Protection: All endpoints secured
2. CORS Enabled: Cross-origin requests allowed
3. Input Validation: Pydantic model validation
4. SQL Injection Protection: Parameterized queries
```
## Error Responses
```
1. 401 Unauthorized
   {
   "detail": "API Key is missing"
   }

   {
   "detail": "Invalid API Key"
   }

2. 500 Internal Server Error

   {
   "detail": "Error message"
   }
```

### Logs
Check application logs for detailed error information and debugging.
