from sqlalchemy import text, TextClause
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


async def execute_sql_query_from_file(file_path: str, params: dict, db_session: AsyncSession) -> Result:
    """
    Reads a SQL query from the specified path and executes it with the given parameters.

    :param file_path: Path to the SQL query file.
    :param params: Dictionary of parameters to substitute in the SQL query.
    :param db_session: AsyncSession to use for executing the query.
    :return: Result of the query execution.
    """
    try:
        with open(file_path, 'r') as file:
            sql_query = file.read()

        query: TextClause = text(sql_query)

        result: Result = await db_session.execute(query, params)

        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        await db_session.rollback()
        raise e
