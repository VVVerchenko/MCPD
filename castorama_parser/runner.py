from scrapy.crawler import CrawlerProcess
from scrapy.utils.reactor import install_reactor
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from castorama_parser.spiders.castoramaru import CastoramaruSpider
import requests
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db_castorama_ru_products = client['db_castorama_ru_products']
product_collection = db_castorama_ru_products.product_collection
session = requests.Session()

if __name__ == '__main__':
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    configure_logging()
    process = CrawlerProcess(get_project_settings())
    process.crawl(CastoramaruSpider, query='люстра')
    process.start()

for items in product_collection.find({}):
    pprint(items)

# подсчитаем количество товаров в БД
products_count = product_collection.count_documents({})

print(f'Товаров в базе: {products_count}')

print()
client.close()

# db_castorama_ru_products.drop_collection('product_collection')