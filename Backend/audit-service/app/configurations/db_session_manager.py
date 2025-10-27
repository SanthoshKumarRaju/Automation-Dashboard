# import contextlib
# from typing import Any, AsyncIterator, Optional
# from sqlalchemy.engine import URL
# from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
# from sqlalchemy.orm import declarative_base
# from app.utils.logger import logging
# from app.configurations.dbconfig import get_connection_url

# BASE = declarative_base()
# logger = logging.getLogger(__name__)

# class DatabaseSessionManager:
#     def __init__(self, host: str, **engine_kwargs):  # CHANGED: host should be string, not URL
#         if engine_kwargs is None:
#             engine_kwargs = {}
#         # CHANGED: Use async engine with async driver
#         self._engine = create_async_engine(host, **engine_kwargs)
#         self._sessionmaker = async_sessionmaker(
#             self._engine, 
#             expire_on_commit=False,
#             class_=AsyncSession
#         )
    
#     async def close(self):
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         await self._engine.dispose()
#         self._engine = None
#         self._sessionmaker = None
    
#     @contextlib.asynccontextmanager
#     async def connect(self) -> AsyncIterator[AsyncConnection]:
#         if self._engine is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         async with self._engine.begin() as connection:
#             try:
#                 yield connection
#             except Exception as e:
#                 await connection.rollback()
#                 logger.error(f"Error during connection: {e}")
#                 raise
    
#     @contextlib.asynccontextmanager
#     async def session(self) -> AsyncIterator[AsyncSession]:
#         if self._sessionmaker is None:
#             raise Exception("DatabaseSessionManager is not initialized")
#         session = self._sessionmaker()
#         try:
#             yield session
#         except Exception as e:
#             await session.rollback()
#             logger.error(f"Error during session: {e}")
#             raise
#         finally:
#             await session.close()

# # Initialize the DatabaseSessionManager with the connection URL string
# url = str(get_connection_url())  # CHANGED: Convert URL to string
# logger.info(f"Database URL: {url}")
# sessionmanager = DatabaseSessionManager(url)

# # Dependency to get a session for async database operations
# async def get_db_session() -> AsyncIterator[AsyncSession]:
#     async with sessionmanager.session() as session:
#         yield session