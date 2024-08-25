from fastapi import APIRouter

from app.loader import db_queries
from app.schemas.parser import QueryDelete
from app_logging import logger

router = APIRouter()


@router.get("/all")
async def all_queries():
    """
    Запрос в бд для всех запросов
    """
    try:
        queries = await db_queries.get_queries()
        return {'status': True,
                'queries': queries,
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False


@router.delete("/query_name")
async def delete_query(request: QueryDelete):
    """
    Запрос в бд для всех запросов
    """
    try:
        query_name = request.query_name
        result = await db_queries.delete_query(query_name)
        return {'status': result,
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False

