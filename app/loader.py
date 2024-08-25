from app.database.tables.google_sheets import GoogleSheets
from app.database.tables.links import Link
from app.database.tables.query import Query
from app.database.tables.seller import Seller

db_links = Link()
db_queries = Query()
db_google_sheets = GoogleSheets()
db_seller = Seller()


async def init_databases():
    await db_links.init_pool()
