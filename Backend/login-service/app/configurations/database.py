import os
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse
from app.utils.logger import get_logger
from app.configurations.config import Settings

# Load settings
settings = Settings()
logger = get_logger(__name__)

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.init_db()
    
    def init_db(self):
        """Initialize database connection"""
        try:
            conn_str = (
                f"DRIVER={settings.sql_driver};"
                f"SERVER={settings.sql_server};"
                f"PORT={settings.sqlserver_port};"
                f"DATABASE={settings.sqlserver_database};"
                f"UID={settings.sqlserver_uid};"
                f"PWD={settings.sqlserver_password};"
                f"TrustServerCertificate=yes"
            )
            
            connect = urllib.parse.quote_plus(conn_str)
            connection_url = f'mssql+pyodbc:///?odbc_connect={connect}'
            
            self.engine = create_engine(
                connection_url, 
                pool_pre_ping=True, 
                pool_recycle=settings.pool_recycle,
                echo=False,
                pool_size=settings.pool_size,
                max_overflow=settings.pool_max_overflow,
                pool_timeout=settings.pool_timeout
            )
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

# Global database instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db():
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()