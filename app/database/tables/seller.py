from typing import Optional
import asyncpg
from app.database.base import BaseDb
from app_logging import logger


class Seller(BaseDb):
    async def get_seller(self) -> Optional[asyncpg.Record] or bool:
        try:
            query = """
                    SELECT * FROM Seller
                    """
            result = await self.fetch(query, )
            return result
        except Exception as e:
            logger.error(f"Error while fetching seller from Database: {e}")
            return False

    async def save_seller_db(self, link: str, seller_name: str) -> bool:
        try:
            query = """
            INSERT INTO Seller (seller_link, seller_name) VALUES ($1, $2)
            ON CONFLICT (seller_link) DO NOTHING
            """
            result = await self.execute(query, link, seller_name)
            return result
        except Exception as e:
            logger.error(f"Error while inserting Seller in Database: {e}")
            return False

    async def get_seller_by_name(self, seller_name: str) -> Optional[asyncpg.Record] or bool:
        try:
            query = """
                    SELECT * FROM Seller where seller_name = ($1)
                    """
            result = await self.fetch(query, seller_name)
            return result
        except Exception as e:
            logger.error(f"Error while fetching Seller from Database: {e}")
            return False

    async def delete_seller(self, seller_name: str) -> bool:
        try:
            seller_id = await self.get_seller_by_name(seller_name)
            seller_id = seller_id[0]['id']
            update_query = """
                                 DELETE FROM Link
                                 where seller_id = $1
                                 """
            result = await self.execute(update_query, seller_id)
            if result:
                query = """
                         DELETE FROM Seller WHERE seller_name = ($1)
                         """
                result = await self.execute(query, seller_name)
                return True if result else False
            raise
        except Exception as e:
            logger.error(f"Error while deleting query from Database: query {seller_name}: {e}")
            return False