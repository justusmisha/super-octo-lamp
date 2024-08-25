import asyncpg
from app_logging import logger


class BaseDb:
    _instance = None
    _pool = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BaseDb, cls).__new__(cls)
        return cls._instance

    async def init_pool(self):
        if BaseDb._pool is None:
            try:

                BaseDb._pool = await asyncpg.create_pool(
                    database='parser_db',
                    user='postgres',
                    password='postgres',
                    host='localhost',
                    port=5432
                )
                logger.info("Database connection pool initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize database pool: {e}")
                raise

    async def fetch(self, query, *args, **kwargs):
        if BaseDb._pool is None:
            raise RuntimeError("Database connection pool not initialized.")
        try:
            async with BaseDb._pool.acquire() as connection:
                async with connection.transaction():
                    return await connection.fetch(query, *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise

    async def execute(self, query, *args, **kwargs):
        if BaseDb._pool is None:
            raise RuntimeError("Database connection pool not initialized.")
        try:
            async with BaseDb._pool.acquire() as connection:
                async with connection.transaction():
                    return await connection.execute(query, *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def close_pool(self):
        if BaseDb._pool is not None:
            try:
                await BaseDb._pool.close()
                BaseDb._pool = None
                logger.info("Database connection pool closed.")
            except Exception as e:
                logger.error(f"Failed to close database pool: {e}")
                raise
