from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import ValidationError
from datetime import datetime
from app.services.auth_service import auth_service
from app.dtos.login_request_dtos import LoginRequest
from app.dtos.login_response_dtos import LoginResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """User login endpoint"""
    try:
        if auth_service.authenticate(login_request.username, login_request.password):
            access_token = auth_service.create_session(login_request.username)
            response = LoginResponse(
                statusCode=200,
                message="Login successful",
                username=login_request.username,
                access_token=access_token,
                timestamp=datetime.now()
            )
            logger.info(f"User: {login_request.username} logged in successfully")
            return response
        else:
            logger.warning(f"Failed login attempt for user: {login_request.username}")
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
            
    except ValidationError as e:
        logger.warning(f"Login validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request data")
    except Exception as e:
        logger.exception(f"Login error:")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout(token: str):
    """User logout endpoint"""
    try:
        # Get current user from token
        current_user = await auth_service.get_current_user(token)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        session_id = current_user.get('session_id')
        username = current_user.get('username')
        
        if not session_id:
            logger.error("No session_id found in current_user")
            raise HTTPException(status_code=400, detail="No active session found")
        
        auth_service.logout(session_id)
        logger.info(f"User: {username} logged out successfully")
        
        return {
            "statusCode": 200,
            "message": "Logout successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Logout error:")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/session/validate")
async def validate_session(current_user: dict = Depends(auth_service.get_current_user)):
    """Validate current session"""
    try:
        # Check if current_user is None (invalid session)
        if not current_user:
            logger.warning("Session validation failed - no valid session found")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired session"
            )
        
        username = current_user.get('username')
        logger.info(f"User: {username} session validated successfully")
        
        return {
            "statusCode": 200,
            "message": "Session validated successfully",
            "username": username,
            "last_seen": datetime.now()
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.exception(f"Session validation error:")
        raise HTTPException(
            status_code=500, 
            detail="Session validation failed"
        )