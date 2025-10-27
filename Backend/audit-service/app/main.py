from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import audit_router
from app.dependencies.api_key_middleware import APIKeyMiddleware 
from app.dependencies.auth_middleware import AuthMiddleware
from app.configurations.settings import Settings
from app.utils.logger import get_logger
from app.dependencies.paths import API_KEY_PATHS, JWT_PATHS, EXCLUDE_PATHS
import uvicorn

logger = get_logger(__name__)
settings = Settings()

# Create middleware instances
api_key_middleware = APIKeyMiddleware()
auth_middleware = AuthMiddleware()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

API_PATH_PREFIX = "/pyaudit"

app = FastAPI(
    docs_url="/pyaudit/docs", 
    redoc_url="/pyaudit/redoc", 
    openapi_url="/pyaudit/openapi.json", 
    description="This is Python Audit Service",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware handler to route based on path
@app.middleware("http")
async def route_middleware(request: Request, call_next):
    path = request.url.path
    
    # Route to appropriate middleware
    if any(path.startswith(api_path) for api_path in API_KEY_PATHS):
        return await api_key_middleware(request, call_next)
    elif any(path.startswith(jwt_path) for jwt_path in JWT_PATHS):
        return await auth_middleware(request, call_next)
    elif any(path.startswith(public_path) for public_path in EXCLUDE_PATHS):
        return await call_next(request)
    else:
        # Default to JWT auth for any other endpoints
        return await auth_middleware(request, call_next)

# Include the routers for different endpoints
app.include_router(audit_router.router, prefix=API_PATH_PREFIX)

# CORRECTED OpenAPI schema configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title="Python Audit Service",
        version="1.0.0",
        description="This is Python Audit Service with mixed authentication (API Key + JWT)",
        routes=app.routes,
    )
    
    # Ensure components section exists
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Add both security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": settings.api_key_name,
            "in": "header"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token from login service"
        }
    }
    
    # Define path-specific security - THIS IS WHAT MAKES THE LOCK ICONS APPEAR
    for path, methods in openapi_schema["paths"].items():
        for method_name, method_details in methods.items():
            full_path = f"/pyaudit{path}" if not path.startswith("/pyaudit") else path
            
            # Skip public paths
            if full_path in EXCLUDE_PATHS:
                continue
            
            # Apply API Key security to create endpoint
            if full_path in API_KEY_PATHS:
                method_details["security"] = [{"APIKeyHeader": []}]
            # Apply JWT security to JWT protected endpoints
            elif full_path in JWT_PATHS:
                method_details["security"] = [{"BearerAuth": []}]
            # Default security for any other endpoints
            else:
                method_details["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)