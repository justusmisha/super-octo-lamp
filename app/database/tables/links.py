from typing import Optional
import asyncpg
from app.database.base import BaseDb
from app_logging import logger


class Link(BaseDb):
    async def get_links(self) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Link
                    """
            result = await self.fetch(query, )
            return result
        except Exception as e:
            logger.error(f"Error while fetching all links from Database: {e}")
            return None

    async def save_links_db(self, link: str, query_id: int) -> bool:
        try:
            query = """
            INSERT INTO Link (link, query_id) VALUES ($1, $2)
            ON CONFLICT (link) DO NOTHING
            """
            result = await self.execute(query, link, query_id)
            return result
        except Exception as e:
            logger.error(f"Error while inserting link: {e}")
            return False

    async def save_seller_links_db(self, link: str, seller_id: int) -> bool:
        try:
            query = """
            INSERT INTO Link (link, seller_id) VALUES ($1, $2)
            ON CONFLICT (link) DO NOTHING
            """
            result = await self.execute(query, link, seller_id)
            return result
        except Exception as e:
            logger.error(f"Error while inserting link: {e}")
            return False

    async def get_links_by_seller_id(self, seller_id: int) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Link where seller_id = $1
                    """
            result = await self.fetch(query, seller_id)
            return result
        except Exception as e:
            logger.error(f"Error while fetching link from Database: {e}")
            return None

    async def get_links_by_query(self, query_id: int) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM Link where query_id = $1
                    """
            result = await self.fetch(query, query_id)
            return result
        except Exception as e:
            logger.error(f"Error while fetching link from Database: {e}")
            return None
