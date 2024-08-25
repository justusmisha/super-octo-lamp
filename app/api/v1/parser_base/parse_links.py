from time import time

import urllib.parse

from fastapi import APIRouter
from app.core.parser.parser import Parser
from app.schemas.parser import OneLink, SaveByQuery, ParserExecute
from app.utils.utils import is_url_encoded
from app.core.excel_downloader import  create_new_sheet
from app.core.parser.link_executor import process_link
from app.loader import db_google_sheets, db_queries
from app_logging import logger

router = APIRouter()


@router.post("/save/by_query")
async def save_links_by_query(request: SaveByQuery):
    """
    Парсит ссылки по запросу и сохраняет в бд
    """

    try:
        query = request.query
        page_numbers = request.page_numbers
        city = request.city
        result = await db_queries.save_query(query)
        if result:
            parser_base = Parser(query=query, page_numbers=page_numbers, city=city)
            result = await parser_base.parse_links()
            if result:
                return {"message": result[0],
                        'time': f'{result[1]:.2f}'}
            else:
                return {"message": result}
        else:
            return {"message": 'Problem with saving fetch to db'}
    except Exception as e:
        raise {"Error": str(e)}


@router.post("/execute")
async def link_executor(request: ParserExecute):
    """
    Парсит ссылки и добавляет их в гугл док
    """
    try:
        query = request.query
        google_sheet_name = request.google_sheet_name
        query = await db_queries.get_id_by_query(query)
        print(query)
        query = query[0]
        print(query)
        start = time()
        google_sheet = await db_google_sheets.get_sheet_by_name(google_sheet_name)
        await create_new_sheet(query['query'], google_sheet['sheet_id'])
        await process_link(sheet=query['query'], sheet_id=google_sheet['sheet_id'], query_id=query['id'])
        end = time()
        length = end - start
        return {'status': True,
                'time': f"{length:.2f}"
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False


@router.post("/one_link")
async def parse_one_link(requets: OneLink):
    """
    Парсит одну ссылку
    """
    try:
        google_sheet_name = requets.google_sheet_name
        url = requets.url
        google_sheet = await db_google_sheets.get_sheet_by_name(google_sheet_name)
        await create_new_sheet('Одиночный запрос', google_sheet['sheet_id'], clear=False)
        start = time()
        await process_link(sheet='Одиночный запрос', sheet_id=google_sheet['sheet_id'], url=url)
        end = time()
        length = end - start
        return {'status': True,
                'time': f"{length:.2f}"
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False
