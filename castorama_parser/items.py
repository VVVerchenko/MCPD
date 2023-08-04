import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst

def process_name(name):
    try:
        name = name[0].strip()
    except Exception as e:
        print(e)
    return name

def process_price(price):
    try:
        price = int(price[2].replace(' ', ''))
    except Exception as e:
        print(e)
    return price

def process_product_code(product_code):
    try:
        product_code = product_code[1]
    except Exception as e:
        print(e)
    return product_code

def process_photo(photo):
    print()
    if photo.startswith('/'):
        photo = "https://www.castorama.ru" + photo
    return photo


class CastoramaParserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=Compose(process_name))
    price = scrapy.Field(input_processor=Compose(process_price), output_processor=TakeFirst())
    product_code = scrapy.Field(output_processor=Compose(process_product_code))
    photos = scrapy.Field(input_processor=MapCompose(process_photo))
    url = scrapy.Field(output_processor=TakeFirst())

