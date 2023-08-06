import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline, FilesPipeline

import requests
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from pprint import pprint
import hashlib
import json

client = MongoClient('127.0.0.1', 27017)
db_avito_products = client['db_avito_products']
product_collection = db_avito_products.product_collection
session = requests.Session()

class AvitoparserPipeline:
    def process_item(self, item, spider):
        # на основе данных товара создадим id
        products_str = json.dumps(str(item['name']) + str(item['url']), sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        products_id = hashlib.md5(products_str.encode()).hexdigest()

        product_final = {}

        product_final['_id'] = products_id

        product_final.update(item)
        # добавим документ product_final в БД
        try:
            product_collection.insert_one(product_final)
        except DuplicateKeyError:
            print(f'Document with id {product_final.get("_id")} already exists')
        return item

class AvitoPhotosPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            yield scrapy.Request(item['photos'])

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item