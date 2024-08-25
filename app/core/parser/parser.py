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
    def __init__(self, page_numbers, query=None, city=None, seller_id=None):
        self.query = query
        self.query_refractored = '+'.join(query.split(' '))
        self.page_numbers = page_numbers
        self.city = city_refractor(city) if city else None
        self.seller_id = seller_id if seller_id else None

    async def parse_links(self):
        try:
            start_time = time()
            if not self.seller_id:
                query_id = await db_queries.get_id_by_query(self.query)
                print(query_id)
                query_id = query_id[0]['id']
                if self.city:
                    for page_number in range(self.page_numbers, 0, -1):
                        targetUrl = f"https://www.avito.ru/{self.city}?q={self.query_refractored}&p={page_number}"
                        print(targetUrl)
                        encoded_url = urllib.parse.quote(targetUrl)
                        url = f"http://api.scrape.do?token={TOKEN}&url={encoded_url}"
                        response = requests.get(url)
                        html_soup = BeautifulSoup(response.text, features="html.parser")
                        divs_with_class = html_soup.find('div', class_='items-items-kAJAg')
                        divs_with_class = divs_with_class.find_all('div', class_='iva-item-root-_lk9K')
                        if not divs_with_class:
                            break
                        for tag in divs_with_class:
                            href_link = tag.find('a', class_='iva-item-sliderLink-uLz1v')
                            if href_link:
                                url = href_link.get("href")
                                parts = url.split('/')
                                new_url = '/' + '/'.join(parts[2:])
                                final_link = f'https://www.avito.ru/{self.city}{new_url}'
                                await db_links.save_links_db(final_link, query_id)
            else:
                for page in range(self.page_numbers, 0, -1):
                    unique_links = set()
                    targetUrl = self.query + f'&p={page}'
                    encoded_url = urllib.parse.quote(targetUrl)
                    url = f"http://api.scrape.do?token={TOKEN}&url={encoded_url}"
                    response = requests.get(url)

                    if response.status_code != 200:
                        logger.error(f"Failed to fetch page {page}. Status code: {response.status_code}")
                        continue

                    html = BeautifulSoup(response.text, 'html.parser')
                    items = 12
                    for item in range(items):
                        divs = html.find_all('div',
                                             {'data-marker': f'item_list_with_filters/item({item})',
                                              'itemscope': '',
                                              'itemtype': 'http://schema.org/Product'})
                        if not divs:
                            break

                        for div in divs:
                            a_tags = div.find_all('a', itemprop='url')
                            for a_tag in a_tags:
                                href = a_tag.get('href')
                                if href not in unique_links:
                                    unique_links.add(href)
                                    if href.startswith("https://www.avito.ru"):
                                        await db_links.save_seller_links_db(seller_id=self.seller_id, link=href)
                                    else:
                                        await db_links.save_seller_links_db(seller_id=self.seller_id, link="https://www.avito.ru" + href)
            end_time = time()
            elapsed_time = end_time - start_time
            return True, int(elapsed_time)
        except Exception as e:
            logger.exception(e)
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

