from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    """Application settings loaded from .env"""
    
    # secret key Configuration
    secret_key: str = Field(..., alias="SECRET_KEY")
    
    # algorithm and access token expire minutes
    algorithm: str = Field(..., alias="ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # logging configurations
    log_file: str = Field(..., alias="LOG_FILE")
    log_level: str = Field(..., alias="LOG_LEVEL")
    log_file_max_bytes: int = Field(..., alias="LOG_FILE_MAX_BYTES")
    log_file_bac_count: int = Field(..., alias="LOG_FILE_BAC_COUNT")

    # sqlserver database configurations
    sql_driver: str = Field(..., alias="SQLSERVER_DRIVER")
    sql_server: str = Field(..., alias="SQL_SERVER")
    sqlserver_uid: str = Field(..., alias="SQLSERVER_UID")
    sqlserver_password: str = Field(..., alias="SQLSERVER_PASSWORD")
    sqlserver_database: str = Field(..., alias="SQLSERVER_DATABASE")
    sqlserver_port: str = Field(..., alias="SQLSERVER_PORT")
    
    # Database Connection pool settings
    pool_size: int = Field(..., alias="POOL_SIZE")
    pool_max_overflow: int = Field(..., alias="POOL_MAX_OVERFLOW")
    pool_recycle: int = Field(..., alias="POOL_RECYCLE")
    pool_timeout: int = Field(..., alias="POOL_TIMEOUT")
    
    # Health Check Login Service url
    health_check_login_service_session_validate_url: str = Field(..., alias="HEALTH_CHECK_LOGIN_SERVICE_SESSION_VALIDATE_URL")
    health_check_login_service_session_validate_url_expire_seconds: int = Field(..., alias="HEALTH_CHECK_LOGIN_SERVICE_SESSION_VALIDATE_URL_EXPIRE_SECONDS")
    
    # Public endpoints that don't require authentication
    public_paths: list = [
        "/pystore/docs",
        "/pystore/redoc", 
        "/pystore/openapi.json",
        "/pystore/api/healthcheck"
    ]

    model_config = ConfigDict(env_file=".env", case_sensitive=True)