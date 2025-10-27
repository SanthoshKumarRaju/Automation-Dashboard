from fastapi import Request
from fastapi.responses import JSONResponse
from app.configurations.settings import Settings
from app.utils.logger import get_logger
from app.dependencies.paths import API_KEY_PATHS

logger = get_logger(__name__)
settings = Settings()

class APIKeyMiddleware:
    def __init__(self):
        # Define API key protected paths here
        self.api_key_paths = API_KEY_PATHS
    
    async def __call__(self, request: Request, call_next):
        # Allow CORS preflight requests through
        if request.method == "OPTIONS":
            logger.debug(f"Skipping API key check for preflight request: {request.url.path}")
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get(settings.api_key_name)
        
        if not api_key:
            logger.warning(f"API Key missing from request to {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "API Key is missing"}
            )
        
        if api_key != settings.api_key:
            logger.warning(f"Invalid API Key provided for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"}
            )
        
        logger.debug(f"API Key validation successful for {request.url.path}")
        response = await call_next(request)
        return response