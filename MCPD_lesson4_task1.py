#______________________________________________________________________________________________________________________
#______________________________________________________________________________________________________________________
# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные новости в БД
#______________________________________________________________________________________________________________________

import requests
from lxml import html
from pprint import pprint

import json
from pymongo import MongoClient
import hashlib
from pymongo.errors import DuplicateKeyError


client = MongoClient('127.0.0.1', 27017)

# создадим указатели на БД
db_lenta_ru_news = client['db_lenta_ru_news']

# создадим коллекцию
hews_collection = db_lenta_ru_news.news
session = requests.Session()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
response = requests.get('https://lenta.ru/', headers=headers)
dom = html.fromstring(response.text)

news_list = []
items = dom.xpath('//a[contains(@class,"card-mini _")]')

for item in items:
    # заполним БД с данными новостей
    news = {}
    news_name = item.xpath('.//h3[@class = "card-mini__title"]//text()')
    link = item.xpath('./@href')
    time = item.xpath('.//time[@class = "card-mini__info-item"]//text()')

    news['news_name'] = news_name
    news['link'] = link
    news['time'] = time
    news['news_source'] = 'https://lenta.ru/'

    # на основе данных новости создадим id
    news_str = json.dumps(news, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    news_id = hashlib.md5(news_str.encode()).hexdigest()
    news_final = {}
    news_final['_id'] = news_id
    news_final.update(news)

    # добавим документ news_final в БД
    try:
        hews_collection.insert_one(news_final)
    except DuplicateKeyError:
        print(f'Document with id {news_final.get("_id")} already exists')

for news in hews_collection.find({}):
    pprint(news)

# подсчитаем количество новостей в БД
vacancies_count = hews_collection.count_documents({})

print(f'Новостей в базе: {vacancies_count}')

client.close()