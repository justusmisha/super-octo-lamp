from time import time

from fastapi import APIRouter

from app.core.excel_downloader import Downloader, create_new_sheet, create_google_dock
from app.core.parser.card_parser import CardParser
from app.core.parser.link_executor import process_link
from app.loader import db_links, db_google_sheets
from app.schemas.google_sheet import GoogleSheet
from app_logging import logger


router = APIRouter()


@router.post("/create")
async def create_sheet(request: GoogleSheet):
    """
    Создает новый гугл документ
    """
    try:
        sheet_name = request.sheet_name
        google_sheets = await db_google_sheets.get_sheets()
        if sheet_name not in google_sheets:
            sheet_id = await create_google_dock(sheet_name)
            await db_google_sheets.save_google_sheet(sheet_name, sheet_id)
            return {'status': True,
                    'sheet_id': str(sheet_id)}
        else:
            return {'status': False}
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False