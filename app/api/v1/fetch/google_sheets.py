from fastapi import APIRouter

from app.loader import db_queries, db_google_sheets
from app.schemas.google_sheet import GoogleSheet
from app_logging import logger

router = APIRouter()


@router.get("/all")
async def get_sheets():
    """

    """
    try:
        google_sheets = await db_google_sheets.get_sheets()
        return {'status': True,
                'sheets': google_sheets}
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False


@router.post("/by_name")
async def get_sheets_by_name(request: GoogleSheet):
    """
    Парсит одну ссылку
    """
    try:
        sheet_name = request.sheet_name
        google_sheet = await db_google_sheets.get_sheet_by_name(sheet_name)
        return {'status': True,
                'sheets': google_sheet}
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False