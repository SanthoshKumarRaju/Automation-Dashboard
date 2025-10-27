from app.configurations.dbconfig import (
    PG_BASE, 
    SQL_BASE, 
    get_postgres_async_engine, 
    get_sqlserver_sync_engine
)

# Functions to initialize databases if not already created for postgreSQL and it is asynchronous
async def initialize_postgres_db_if_not_created():
    """Initialize PostgreSQL database tables"""
    engine = get_postgres_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(PG_BASE.metadata.create_all)
    await engine.dispose()

# Functions to initialize databases if not already created for SQL Server and it is synchronous
def initialize_sqlserver_db_if_not_created():
    """Initialize SQL Server database tables"""
    engine = get_sqlserver_sync_engine()
    SQL_BASE.metadata.create_all(engine)
    engine.dispose()