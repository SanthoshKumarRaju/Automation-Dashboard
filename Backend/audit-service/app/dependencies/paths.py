# path definitions for authentication

# API Key protected endpoints
API_KEY_PATHS = [
    "/pyaudit/api/audit-events/create"
]

# JWT protected endpoints  
JWT_PATHS = [
    "/pyaudit/api/audit-events/recent",
    "/pyaudit/api/audit-events/get-eventtypenames-by-functionalityname",
    "/pyaudit/api/audit-events/search",
    "/pyaudit/api/audit-events/get-all-auditfunctionalities",
    "/pyaudit/api/audit-events/export",
    "/pyaudit/api/audit-events/get-all-companies",
    "/pyaudit/api/audit-events/get-storelocations-by-company"
]

# Public endpoints (no auth)
EXCLUDE_PATHS = [
    "/pyaudit/docs",
    "/pyaudit/redoc", 
    "/pyaudit/openapi.json",
    "/pyaudit/api/healthcheck"
]