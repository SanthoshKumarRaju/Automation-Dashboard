from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.utils.logger import get_logger
from app.routers import auth_routes, health_routes
import os
import uvicorn

# Initialize logger
logger = get_logger(__name__)

# api path prefix
API_PATH_PREFIX = "/pylogin"

# Lifespan event for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up HealthCheck Login Dashboard API...")
    yield
    # Shutdown
    logger.info("Shutting down HealthCheck Login Dashboard API")

app = FastAPI(
     title="Login Service HealthCheck Dashboard",
    description="Login Service HealthCheck Dashboard",
    docs_url="/pylogin/docs",
    redoc_url="/pylogin/redoc",
    openapi_url="/pylogin/openapi.json",
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

# Include routers with full prefix
app.include_router(auth_routes.router, prefix=f"{API_PATH_PREFIX}", tags=["authentication"])
app.include_router(health_routes.router, prefix=f"{API_PATH_PREFIX}", tags=["health"])

# Run the application    
if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000
    logger.info(f"Starting HealthCheck Login Dashboard API on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
    