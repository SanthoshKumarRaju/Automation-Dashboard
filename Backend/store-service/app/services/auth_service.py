import uuid
import glob
import os
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.apache import HtpasswdFile
from app.utils.logger import get_logger
from app.configurations.config import Settings

logger = get_logger(__name__)
settings = Settings()

class AuthService:
    def __init__(self):
        self.ht = None
        self.active_sessions = {}
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.init_auth()
    
    def init_auth(self):
        """Initialize authentication service"""
        try:
            htpasswd_path = os.path.join(os.path.dirname(__file__), '..', '..', '.htpasswd')
            if not os.path.exists(htpasswd_path):
                logger.warning(f".htpasswd file not found at {htpasswd_path}")
                self.ht = HtpasswdFile()
                self.ht.set_password("admin", "jaya123")
                self.ht.set_password("cstoreiq", "jaya@123")
                self.ht.save(htpasswd_path)
                logger.info("Default .htpasswd file created with development credentials")
            else:
                self.ht = HtpasswdFile(htpasswd_path)
                logger.info("Loaded existing .htpasswd file")
            
        except Exception as e:
            logger.error(f"Failed to initialize auth service: {str(e)}")
            raise
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        try:
            if self.ht and self.ht.check_password(username, password):
                return True
            logger.warning(f"Failed authentication attempt for user: {username}")
            return False
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {str(e)}")
            return False
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def create_session(self, username: str):
        """Create user session"""
        session_id = str(uuid.uuid4())
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": username, "session_id": session_id},
            expires_delta=access_token_expires
        )
        
        self.active_sessions[session_id] = {
            "username": username,
            "created_at": datetime.now(timezone.utc),
            "last_seen": datetime.now(timezone.utc)
        }
        
        return access_token
    
    def validate_session(self, token: str):
        """Validate session token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        session_id = payload.get("session_id")
        if session_id not in self.active_sessions:
            return None
        
        # Update last seen
        self.active_sessions[session_id]["last_seen"] = datetime.now(timezone.utc)
        return self.active_sessions[session_id]
    
    def logout(self, session_id: str):
        """Logout user and clear session"""
        try:
            if session_id in self.active_sessions:
                username = self.active_sessions[session_id]["username"]
                del self.active_sessions[session_id]
                logger.info(f"User {username} logged out")
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
    
    def get_active_sessions_count(self):
        """Get count of active sessions"""
        return len(self.active_sessions)
    
    async def get_current_user(self, token: str):
        """FastAPI dependency to get current user"""
        user_data = self.validate_session(token)
        if not user_data:
            return None
        return user_data

# Global auth service instance
auth_service = AuthService()