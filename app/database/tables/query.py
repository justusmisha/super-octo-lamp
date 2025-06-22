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
    
    async def get_query_by_id(self, query_id: int) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Query WHERE id = ($1)
                    """
            result = await self.fetch(query, query_id)

            return result
        except Exception as e:
            logger.error(f"Error while fetching fetch from Database: fetch {query_id}: {e}")
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

    async def delete_query(self, query_id: str) -> bool:
        try:
            query_id_row = await self.get_query_by_id(int(query_id))

            if not query_id_row:
                logger.warning(f"No query found in DB with text: {query_id}")
                return False

            query_str = query_id_row[0]['query']

            delete_links_query = """
                DELETE FROM Link WHERE query_str = $1
            """
            await self.execute(delete_links_query, query_str)

            delete_query = """
                DELETE FROM Query WHERE query = $1
            """
            result_query = await self.execute(delete_query, query_str)

            return bool(result_query)
        except Exception as e:
            logger.error(f"Error while deleting query from Database: query {query_str}: {e}")
            return False