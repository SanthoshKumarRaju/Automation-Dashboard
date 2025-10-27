from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.dependencies.auth_middleware import auth_middleware
from app.utils.logger import get_logger
from app.configurations.config import Settings
from app.routers import data_routes, export_routes, health_routes
import uvicorn

# Initialize logger
logger = get_logger(__name__)

# Initialize settings
settings = Settings()

# API path prefix
API_PATH_PREFIX = "/pystore"

# Lifespan event for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up HealthCheck Store Service Dashboard API...")
    yield
    # Shutdown
    logger.info("Shutting down HealthCheck Store Service Dashboard API")

app = FastAPI(
    title="Store Service HealthCheck Dashboard",
    description="Store Service HealthCheck Dashboard API with JWT Authentication",
    docs_url=f"{API_PATH_PREFIX}/docs",
    redoc_url=f"{API_PATH_PREFIX}/redoc",
    openapi_url=f"{API_PATH_PREFIX}/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware AFTER CORS
app.middleware("http")(auth_middleware)

# Include routers with full prefix
app.include_router(data_routes.router, prefix=f"{API_PATH_PREFIX}", tags=["data"])
app.include_router(export_routes.router, prefix=f"{API_PATH_PREFIX}", tags=["export"])
app.include_router(health_routes.router, prefix=f"{API_PATH_PREFIX}", tags=["health"])

# Custom OpenAPI configuration to add security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Get the base OpenAPI schema without recursion
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version if hasattr(app, 'version') else "1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from login service"
        }
    }
    
    # Use public paths from config
    public_paths = settings.public_paths
    for path, methods in openapi_schema["paths"].items():
        # Skip public paths
        if any(public_path in path for public_path in public_paths):
            continue
            
        for method in methods.values():
            if isinstance(method, dict):
                method["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Assign the custom OpenAPI function
app.openapi = custom_openapi

# Run the application    
if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000
    logger.info(f"Starting HealthCheck Dashboard store service API on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)