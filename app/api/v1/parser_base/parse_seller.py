from time import time

from fastapi import APIRouter

from app.core.excel_downloader import Downloader, create_new_sheet
from app.core.parser.card_parser import CardParser, browser_parser
from app.core.parser.link_executor import process_link
from app.core.parser.parser import ProfileParser, Parser
from app.loader import db_links, db_google_sheets, db_queries, db_seller
from app.schemas.parser import AddSeller, ParseSeller
from app_logging import logger

router = APIRouter()


@router.post("/add")
async def save_seller(request: AddSeller):
    """
    Добавляет Продавца в бд
    """
    try:
        url = request.url
        parser = ProfileParser(browser_parser(url))
        start = time()
        name = await parser.get_name_profile()
        await db_seller.save_seller_db(url, name)
        end = time()
        length = end - start
        return {'status': True,
                'time': f"{length:.2f}",
                'seller_name': name
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False


@router.post("/parse")
async def parse_seller(request: ParseSeller):
    """
    Парсит продавца
    """
    try:
        seller_name = request.seller_name
        page_numbers = request.page_numbers
        google_sheet = request.google_sheet
        seller = await db_seller.get_seller_by_name(seller_name)
        google_sheet = await db_google_sheets.get_sheet_by_name(google_sheet)
        await create_new_sheet(seller_name, google_sheet['sheet_id'])
        start = time()
        parser = Parser(page_numbers, query=seller[0]['seller_link'], seller_id=seller[0]['id'])
        result = await parser.parse_links()
        if result:
            await process_link(sheet=seller_name, sheet_id=google_sheet['sheet_id'], seller_id=seller[0]['id'])
            end = time()
            length = end - start
            return {'status': True,
                    'time': f"{length:.2f}"
                    }
        return {'status': False}
    except Exception as e:
        logger.error(f'Error in parsing Seller: {e}')
        return False
