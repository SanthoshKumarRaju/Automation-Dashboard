from fastapi import Request
from fastapi.responses import JSONResponse
import requests
from app.configurations.config import Settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = Settings()

class AuthMiddleware:
    def __init__(self):
        logger.info("Auth Middleware initialized")
        # Build session validation URL from health check URL
        self.validate_url = settings.health_check_login_service_session_validate_url
        self.public_paths = settings.public_paths
    
    async def validate_token(self, token: str) -> dict:
        """Validate JWT token by calling login service session validation"""
        try:
            # Call session validation endpoint with token as query parameter
            response = requests.get(
                self.validate_url,
                params={"token": token},
                timeout=settings.health_check_login_service_session_validate_url_expire_seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("statusCode") == 200:
                    return {
                        'username': data.get('username'),
                        'last_seen': data.get('last_seen'),
                        'validated': True
                    }
            
            logger.warning(f"Session validation failed: {response.status_code}, response:{response.text}")
            return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Login service unavailable: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    async def __call__(self, request: Request, call_next):
        
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip auth for public endpoints
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # Check for auth header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authorization header"}
            )
        
        # Extract token
        try:
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
            else:
                parts = auth_header.split()
                if len(parts) != 2 or parts[0].lower() != "bearer":
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid authentication scheme"}
                    )
                token = parts[1]
            
            # Validate token with login service
            user_data = await self.validate_token(token)
            if not user_data:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )
            
            # Add user to request state
            request.state.user = user_data
            logger.info(f"User {user_data['username']} accessed {request.url.path}")
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed"}
            )

# Create instance
auth_middleware = AuthMiddleware()