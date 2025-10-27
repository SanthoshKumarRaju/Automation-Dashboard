import asyncio
import asyncpg
from app.configurations.settings import Settings

settings = Settings()

async def test_connection():
    try:
        # Connect to PostgreSQL using asyncpg directly
        conn = await asyncpg.connect(
            host=settings.host,
            port=settings.port,
            database=settings.dbname,
            user=settings.username,
            password=settings.password
        )
        
        print("PostgreSQL connection successful")
        
        # Test a simple query with asyncpg
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version}")
        
        # Test health check query
        status = await conn.fetchval('SELECT 1 as status')
        print(f"Health check status: {status}")
        
        await conn.close()
        print("Database health check completed successfully.")
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_connection())
    print(f"Connection test passed: {result}")

    '''
    To test the connection : 
        Support Dashboard\supportdashboard\Backend\audit-service> python -m app.tests.test_postgresql_connection
    Expected output:
        PostgreSQL connection successful
        PostgreSQL version: PostgreSQL 17.4 on aarch64-unknown-linux-gnu, compiled by gcc (GCC) 12.4.0, 64-bit
        Health check status: 1
        Database health check completed successfully.
        Connection test passed: True
    '''