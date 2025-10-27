# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from app.services.auth_service import auth_service
# from app.utils.logger import get_logger

# # initilize logger
# logger = get_logger(__name__)
# security = HTTPBearer()

# # This function is used to get the current user
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Dependency to get current user from token/session"""
#     try:
#         token = credentials.credentials
#         user = auth_service.validate_session(token)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid authentication credentials",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return user
#     except Exception as e:
#         logger.exception(f"Authentication error:")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication required",
#         )

# # This function is used to check the dependency for requiring admin privileges
# async def admin_required(current_user: dict = Depends(get_current_user)):
#     """Dependency for requiring admin privileges"""
#     if current_user.get('username') not in ['admin']:
#         logger.warning(f"Admin access denied for user: {current_user.get('username')}")
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admin privileges required"
#         )
#     return current_user