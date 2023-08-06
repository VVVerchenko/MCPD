import requests
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db_avito_products = client['db_avito_products']
product_collection = db_avito_products.product_collection
session = requests.Session()


for items in product_collection.find({}):
    pprint(items)

# подсчитаем количество товаров в БД
products_count = product_collection.count_documents({})

print(f'Товаров в базе: {products_count}')

print()
client.close()
print()
# db_avito_products.drop_collection('product_collection')

