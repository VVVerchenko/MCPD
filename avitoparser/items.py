# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst

def process_price(price):
    try:
        price = int(price[0].replace('\xa0',''))
    except Exception:
        price = None
    return price

def process_currency(currency):
    try:
        currency = currency[0].replace('\xa0', '')
    except Exception:
        currency = None
    return currency

def process_photos(photos):
    try:
        photos = photos[0] + '.jpg'
    except Exception:
        photos = None
    return photos

class AvitoparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    seller = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(process_price), output_processor=TakeFirst())
    currency = scrapy.Field(input_processor=Compose(process_currency), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=Compose(process_photos), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    print()




