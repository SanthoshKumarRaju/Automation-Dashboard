# import json
# import boto3
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import declarative_base
# from sqlalchemy.pool import AsyncAdaptedQueuePool

# from app.configurations.settings import Settings
# from app.utils.logger import logging

# logger = logging.getLogger(__name__)

# BASE = declarative_base()

# # Use local settings
# settings = Settings()

# # Determine database environment
# db_env = settings.db_env

# # AWS Secrets Manager key for audit PostgreSQL database
# aws_audit_pg_db_keys = settings.aws_audit_pg_db_keys

# # Function to construct the database connection URL
# def get_connection_url():
#     logger.info(f"load_env_data: {db_env}")
#     if db_env == "local":
        
#         server = settings.host
#         port = settings.port
#         database = settings.dbname
#         uid = settings.username
#         pwd = settings.password
        
#         # PostgreSQL connection URL
#         url = f"postgresql+asyncpg://{uid}:{pwd}@{server}:{port}/{database}"

#     else:
#         # Fetch secrets from AWS Secrets Manager
#         client = boto3.client("secretsmanager", region_name="us-east-1")
#         response = client.get_secret_value(SecretId=aws_audit_pg_db_keys)
#         database_secrets = json.loads(response["SecretString"])
#         server = database_secrets["pghost"]
#         port = database_secrets["pgport"]
#         database = database_secrets["pgdbname"]
#         uid = database_secrets["pgusername"]
#         pwd = database_secrets["pgpassword"]
        
#         # PostgreSQL connection URL
#         url = f"postgresql+asyncpg://{uid}:{pwd}@{server}:{port}/{database}"
    
#     logger.info(f"construct url: {url}")
#     return url

# # Create async engine with connection pooling
# def get_async_engine():
#     url = get_connection_url()
#     return create_async_engine(
#         url, 
#         # NECESSARY: Pool size configuration (crucial for performance)
#         pool_size=settings.pool_size,                  # MIN POOL SIZE: Minimum number of connections to maintain: 5
#         max_overflow=settings.pool_max_overflow,       # MAX POOL SIZE: pool_size + max_overflow = 15 total max connections
        
#         # HIGHLY RECOMMENDED: Connection health checking
#         pool_recycle=settings.pool_recycle,            # Recycle connections after 30 minutes to prevent database timeouts
#         pool_pre_ping=True,                            # Test connection liveliness before use (prevents connection errors)
        
#         # RECOMMENDED: Timeout settings
#         pool_timeout=settings.pool_timeout,            # Wait up to 30 seconds for a connection from the pool
        
#         # OPTIONAL: Default behavior (can be omitted)
#         poolclass=AsyncAdaptedQueuePool,               # Default async pool class (optional to specify)
#         echo=False,                                    # Set to True only for development/debugging (SQL logging)
#         future=True                                    # Future compatibility (default in SQLAlchemy 2.0+)
#     )

# def get_async_session():
#     engine = get_async_engine()
#     return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# # Dependency for FastAPI
# async def get_db():
#     async_session = get_async_session()
#     async with async_session() as session:
#         try:
#             yield session
#         finally:
#             await session.close()

# dbconfig.py - Fix BASE declarations
import json
import boto3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

from app.configurations.settings import Settings
from app.utils.logger import logging

logger = logging.getLogger(__name__)

# Separate Base classes for different databases
PG_BASE = declarative_base()  # For PostgreSQL models
SQL_BASE = declarative_base() # For SQL Server models

settings = Settings()
db_env = settings.db_env
aws_audit_pg_db_keys = settings.aws_audit_pg_db_keys

# ==================== POSTGRESQL CONFIGURATION (ASYNC) ====================
def get_postgres_connection_url():
    """Get PostgreSQL connection URL"""
    logger.info(f"load_env_data: {db_env}")
    if db_env == "local":
        url = f"postgresql+asyncpg://{settings.pg_username}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_dbname}"
    else:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=aws_audit_pg_db_keys)
        database_secrets = json.loads(response["SecretString"])
        server = database_secrets["pghost"]
        port = database_secrets["pgport"]
        database = database_secrets["pgdbname"]
        uid = database_secrets["pgusername"]
        pwd = database_secrets["pgpassword"]
        
        url = f"postgresql+asyncpg://{uid}:{pwd}@{server}:{port}/{database}"
    
    logger.info(f"construct url: {url}")
    return url

def get_postgres_async_engine():
    """Create async engine for PostgreSQL"""
    url = get_postgres_connection_url()
    return create_async_engine(
        url,
        pool_size=settings.pool_size,
        max_overflow=settings.pool_max_overflow,
        pool_recycle=settings.pool_recycle,
        pool_pre_ping=True,
        pool_timeout=settings.pool_timeout,
        poolclass=AsyncAdaptedQueuePool,
        echo=False,
        future=True
    )

def get_postgres_async_session():
    """Create async session factory for PostgreSQL"""
    engine = get_postgres_async_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# PostgreSQL Dependency for FastAPI
async def get_postgres_db():
    """Dependency to get PostgreSQL database session"""
    async_session = get_postgres_async_session()
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# ==================== SQL SERVER CONFIGURATION (SYNC - Since models are sync) ====================

def get_sqlserver_connection_string():
    """Get SQL Server ODBC connection string"""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.sql_server};"
        f"PORT={settings.sqlserver_port};"
        f"DATABASE={settings.sqlserver_database};"
        f"UID={settings.sqlserver_uid};"
        f"PWD={settings.sqlserver_password};"
        f"TrustServerCertificate=yes"
    )
    return connection_string

def get_sqlserver_sync_engine():
    """Create sync engine for SQL Server (since company/store models are sync)"""
    connection_string = get_sqlserver_connection_string()
    url = URL.create(
        "mssql+pyodbc", 
        query={"odbc_connect": connection_string}
    )
    return create_engine(url)

def get_sqlserver_sync_session():
    """Create sync session factory for SQL Server"""
    engine = get_sqlserver_sync_engine()
    return sync_sessionmaker(engine, expire_on_commit=False)

# SQL Server Dependency for FastAPI (sync)
def get_sqlserver_db():
    """Sync dependency for SQL Server"""
    session_factory = get_sqlserver_sync_session()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()