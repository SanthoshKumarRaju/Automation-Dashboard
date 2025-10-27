from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.configurations.dbconfig import get_postgres_db, get_sqlserver_db

# PostgreSQL session dependency (async)
PostgresDBSession = Annotated[AsyncSession, Depends(get_postgres_db)]

# SQL Server session dependency (sync)
SqlServerDBSession = Annotated[Session, Depends(get_sqlserver_db)]