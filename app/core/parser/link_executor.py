import time

from app.core.parser.card_parser import CardParser
from app.core.excel_downloader import Downloader
from app.loader import db_links, db_seller
from app_logging import logger


async def process_link(sheet=None, sheet_id=None, query_id=None, seller_id: int = None, url:str=None):
    try:
        if url:
            await card_parser_usage(sheet, sheet_id, url, idx=1)
        elif seller_id is not None:
            links = await db_links.get_links_by_seller_id(seller_id)
            for idx, link in enumerate(links, start=1):
                await card_parser_usage(sheet, sheet_id, link['link'], idx=idx)
        else:
            links = await db_links.get_links_by_query(query_id)
            for idx, link in enumerate(links, start=1):
                await card_parser_usage(sheet, sheet_id, link['link'], idx)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


async def card_parser_usage(sheet, sheet_id, link, idx=None):
    try:
        parser = CardParser(url=link)
        profile_link = await parser.get_profile_link()
        profile_link = profile_link if isinstance(profile_link, str) else ''
        downloader = Downloader(
            title=await parser.get_title(),
            geo=await parser.get_geo(),
            number=await parser.get_number(),
            views=await parser.get_views(),
            description=await parser.get_description(),
            description_html=await parser.get_description_html(),
            photos=await parser.get_photos(),
            profile_link=profile_link,
            product_link=await parser.get_product_link(),
            rating=await parser.get_rating()
        )
        range_start = f"{sheet}!A{idx}:H{idx}"
        print(range_start)
        downloader.export_to_google(sheet_id, range_start, "USER_ENTERED")
    except Exception as e:
        logger.warn(f"Failed to process link {link}: {e}")
