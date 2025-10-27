
from fastapi import APIRouter

router = APIRouter(prefix='/api')

# This endpoint provides basic healthcheck information
@router.get("/healthcheck")
async def root():
    """Root endpoint with healthcheck information"""
    return {
        "Status": "healthy",
        "message": "Python healthcheck login-service is running successfully"
    }