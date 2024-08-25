from typing import Optional, Any
import asyncpg
from app.database.base import BaseDb
from app_logging import logger


class GoogleSheets(BaseDb):
    async def get_sheet_by_name(self, sheet_name: str) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM google_sheets WHERE sheet_name = ($1)
                    """
            result = await self.fetch(query, sheet_name)

            return result[0]
        except Exception as e:
            logger.error(f"Error while fetching query from Database: sheet name is {sheet_name}: {e}")
            return None

    async def get_sheets(self) -> Optional[asyncpg.Record]:
        try:
            query = """
                    SELECT * FROM google_sheets
                    """
            result = await self.fetch(query, )

            return result
        except Exception as e:
            logger.error(f"Error while fetching query from Database when fetch Google Sheets: {e}")
            return None

    async def save_google_sheet(self, sheet_name: str, sheet_id: str) -> bool:
        try:
            query = """
                INSERT INTO google_sheets (sheet_id, sheet_name) values ($1, $2)
                ON CONFLICT (sheet_name) DO NOTHING
            """
            result = await self.execute(query,  sheet_id, sheet_name)
            return True
        except Exception as e:
            logger.error(f"Error while inserting Google Sheet into Database: Sheet name: {sheet_name} {e}")
            return False