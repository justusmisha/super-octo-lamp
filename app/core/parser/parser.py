from concurrent.futures import ThreadPoolExecutor
import asyncio
import math
import urllib.parse
import requests
from time import time
from bs4 import BeautifulSoup

from app.core.parser.card_parser import browser_parser
from app.database.data.config import TOKEN
from app.loader import db_links, db_queries, db_seller
from app.utils.city_translate import city_refractor
from app.utils.utils import is_url_encoded
from app_logging import logger


class Parser:
    def __init__(self, page_numbers, query=None, city=None, seller_id=None, max_threads=10):
        self.query = query
        self.query_refractored = '+'.join(query.split(' ')) if query else None
        self.page_numbers = int(page_numbers) if page_numbers != 'all' else self.page_counter()
        self.city = city_refractor(city) if city else None
        self.seller_id = seller_id if seller_id else None
        self.executor = ThreadPoolExecutor(max_threads)

    def page_counter(self):
        try:
            encoded_url = urllib.parse.quote(self.query)
            targetUrl = f"http://api.scrape.do?token={TOKEN}&url={encoded_url}"
            response = requests.get(targetUrl)
            html = BeautifulSoup(response.text, 'html.parser')
            tab_button = html.find('span', class_='styles-module-tab-button-title-_fs7m')
            if tab_button and tab_button.get_text(strip=True) == 'Активные':
                counter_span = html.find('span', class_='styles-module-counter-qyO5b')
                if counter_span:
                    counter_value = counter_span.get_text(strip=True)
                    counter_value = int(counter_value) / 12
                    return math.ceil(counter_value)
                else:
                    logger.error('Counter span not found')
                    return None
            logger.error('No span named Активные')
            return None
        except Exception as e:
            logger.error(f'Error occurred in page counter: {e}')
            return False

    async def fetch_page(self, url):
        """Fetch a page using a thread in the executor."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(self.executor, requests.get, url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
            return None
        return BeautifulSoup(response.text, 'html.parser')

    async def process_page(self, url, query_id=None, seller_id=None):
        """
        Process a single page, extracting links.
        """
        html_soup = await self.fetch_page(url)
        if not html_soup:
            return

        unique_links = set()
        div_class, link_class = self._get_classes(query_id)

        divs = html_soup.find_all('div', class_=div_class)
        for div in divs:
            href = self._extract_link(div, link_class)
            if href and href not in unique_links:
                unique_links.add(href)
                await self._save_link(href, query_id, seller_id)

    def _get_classes(self, query_id):
        """
        Return the appropriate div and link class based on query_id.
        """
        if query_id:
            return 'iva-item-body-GQomw', 'styles-module-root-m3BML styles-module-root_noVisited-HHF0s'
        return 'body-root-vycQ5', 'styles-module-root-iSkj3 styles-module-root_noVisited-qJP5D'

    def _extract_link(self, div, link_class):
        """
        Extract and format the link from the given div.
        """
        href_tag = div.find('a', class_=link_class)
        if not href_tag:
            return None
        href = href_tag.get("href")
        if href:
            return f"https://www.avito.ru{href}" if not href.startswith("https") else href
        return None

    async def _save_link(self, link, query_id=None, seller_id=None):
        """
        Save the extracted link to the database based on query_id or seller_id.
        """
        if query_id:
            await db_links.save_links_db(link, query_id)
        elif seller_id:
            await db_links.save_seller_links_db(seller_id=seller_id, link=link)

    async def parse_links(self):
        try:
            start_time = time()

            def build_scrape_url(target_url):
                """Encodes the target URL and appends the scraping API token."""
                encoded_url = urllib.parse.quote(target_url)
                return f"http://api.scrape.do?token={TOKEN}&url={encoded_url}"

            urls = []
            if not self.seller_id:
                query_id = await db_queries.get_id_by_query(self.query)
                query_id = query_id[0]['id']
                print(query_id)
                if self.city:
                    for page_number in range(self.page_numbers, 0, -1):
                        target_url = f"https://www.avito.ru/{self.city}?localPriority=0&q={self.query_refractored}&p={page_number}"
                        print(target_url)
                        urls.append(build_scrape_url(target_url))
            else:
                for page_number in range(self.page_numbers):
                    target_url = f"{self.query}&p={page_number}"
                    urls.append(build_scrape_url(target_url))

            tasks = [self.process_page(url, query_id=query_id if not self.seller_id else None, seller_id=self.seller_id) for url in urls]
            await asyncio.gather(*tasks)

            elapsed_time = time() - start_time
            return True, int(elapsed_time)
        except Exception as e:
            logger.exception("An error occurred during parsing.")
            return False


class ProfileParser:

    def __init__(self, html_source):
        self.html_source = html_source
        for name in self.html_source.find_all('h1'):
            if name.text == 'Объявления пользователя скрыты':
                self.validation = False
                break
            else:
                self.validation = True
                break

    async def get_name_profile(self):
        if self.validation:
            names = self.html_source.find_all('div', class_='AvatarNameView-name-UrFI_')
            for name in names:
                h1_name = name.find('h1').text.strip()
                return h1_name
        return False