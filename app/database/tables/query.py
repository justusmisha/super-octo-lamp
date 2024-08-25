from typing import Optional
import asyncpg
from app.database.base import BaseDb

from app_logging import logger


class Query(BaseDb):
    async def get_id_by_query(self, query_str: str) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Query WHERE query = ($1)
                    """
            result = await self.fetch(query, query_str)

            return result
        except Exception as e:
            logger.error(f"Error while fetching fetch from Database: fetch {query_str}: {e}")
            return None

    async def save_query(self, query_str: str) -> bool:
        try:
            query = """
                INSERT INTO Query (query) values ($1)
                ON CONFLICT (query) DO NOTHING
            """
            await self.execute(query,  query_str)
            return True
        except Exception as e:
            logger.error(f"Error while inserting fetch into Database: fetch: {query_str}: {e}")
            return False

    async def get_queries(self) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Query
                    """
            result = await self.fetch(query, )

            return result
        except Exception as e:
            logger.error(f"Error while fetching fetch from Database: all queries: {e}")
            return None

    async def delete_query(self, query_str: str) -> bool:
        try:
            query_id = await self.get_id_by_query(query_str)
            query_id = query_id[0]['id']
            update_query = """
                                DELETE FROM Link
                                where query_id = $1
                                """
            result = await self.execute(update_query, query_id)
            if result:
                query = """
                        DELETE FROM Query WHERE query = ($1)
                        """
                result = await self.execute(query, query_str)
                return True if result else False
            raise
        except Exception as e:
            logger.error(f"Error while deleting query from Database: query {query_str}: {e}")
            return False