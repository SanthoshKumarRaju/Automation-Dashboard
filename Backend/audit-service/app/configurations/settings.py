from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env"""
    
    # postgresql database configurations
    pg_host: str = Field(..., alias="PG_HOST")
    pg_port: str = Field(..., alias="PG_PORT")
    pg_dbname: str = Field(..., alias="PG_DATABASE")
    pg_username: str = Field(..., alias="PG_USER")
    pg_password: str = Field(..., alias="PG_PASSWORD")
    
    # sqlserver database configurations
    sql_server: str = Field(..., alias="SQL_SERVER")
    sqlserver_uid: str = Field(..., alias="SQLSERVER_UID")
    sqlserver_password: str = Field(..., alias="SQLSERVER_PASSWORD")
    sqlserver_database: str = Field(..., alias="SQLSERVER_DATABASE")
    sqlserver_port: str = Field(..., alias="SQLSERVER_PORT")

    # log level
    log_level: str = Field(..., alias="LOG_LEVEL")
    
    # Environment configuration
    db_env: str = Field(..., alias="DB_ENV")
    
    # audit postgresql database keys in AWS Secrets Manager
    aws_audit_pg_db_keys: str = Field(..., alias="AWS_AUDIT_PG_DB_KEYS")
    
    # Database Connection pool settings
    pool_size: int = Field(..., alias="POOL_SIZE")
    pool_max_overflow: int = Field(..., alias="POOL_MAX_OVERFLOW")
    pool_recycle: int = Field(..., alias="POOL_RECYCLE")
    pool_timeout: int = Field(..., alias="POOL_TIMEOUT")
    
    # API Key settings
    api_key: str = Field(..., alias="CSIQ_API_KEY")
    api_key_name: str = Field(..., alias="API_KEY_NAME")
    
    # logging settings log name, max bytes, backup count
    log_file_name: str = Field(..., alias="LOG_FILE_NAME")
    log_file_max_bytes: int = Field(..., alias="LOG_FILE_MAX_BYTES")
    log_file_bac_count: int = Field(..., alias="LOG_FILE_BAC_COUNT")
    
    # Health Check Login Service url
    health_check_login_service_session_validate_url: str = Field(..., alias="HEALTH_CHECK_LOGIN_SERVICE_SESSION_VALIDATE_URL")
    health_check_login_service_session_validate_url_expire_seconds: int = Field(..., alias="HEALTH_CHECK_LOGIN_SERVICE_SESSION_VALIDATE_URL_EXPIRE_SECONDS")

    model_config = ConfigDict(env_file=".env", case_sensitive=True)
