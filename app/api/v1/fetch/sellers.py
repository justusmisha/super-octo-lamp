from fastapi import APIRouter

from app.loader import db_seller
from app.schemas.parser import SellerDelete
from app_logging import logger

router = APIRouter()


@router.get("/all")
async def all_queries():
    """
    Запрос в бд для всех продавцов
    """
    try:
        sellers = await db_seller.get_seller()
        return {'status': True,
                'sellers': sellers,
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False


@router.delete("/seller_name")
async def delete_query(request: SellerDelete):
    """
    Запрос в бд для всех запросов
    """
    try:
        seller_name = request.seller_name
        result = await db_seller.delete_seller(seller_name)
        return {'status': result,
                }
    except Exception as e:
        logger.error(f'Error in link executor: {e}')
        return False
