
from fastapi import APIRouter, Depends, HTTPException
from app.configurations.database import db_manager, get_db
from app.services.data_service import data_service
from app.services.export_service import export_service
from app.utils.logger import get_logger
from app.dependencies.auth_middleware import auth_middleware

# logger initialization
logger = get_logger(__name__)

router = APIRouter(prefix='/api')
pathprefix = "/pystore"

# This endpoint provides basic healthcheck information
@router.get("/healthcheck")
async def root():
    """Root endpoint with healthcheck information"""
    return {
        "Status": "healthy",
        "message": "Python healthcheck store-service is running successfully"
    }