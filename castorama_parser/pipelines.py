import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline, FilesPipeline

import requests
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db_castorama_ru_products = client['db_castorama_ru_products']
product_collection = db_castorama_ru_products.product_collection
session = requests.Session()

class CastoramaParserPipeline:
    def process_item(self, item, spider):
        # на основе данных товара создадим id
        product_final = {}
        product_final['_id'] = item['product_code']
        product_final.update(item)
        # добавим документ letters_final в БД
        try:
            product_collection.insert_one(product_final)
        except DuplicateKeyError:
            print(f'Document with id {product_final.get("_id")} already exists')
        return item

# class CastoramaPhotosPipeline(ImagesPipeline): # с этим кодом не получилось скачать фото
class CastoramaPhotosPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


