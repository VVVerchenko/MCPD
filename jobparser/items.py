import scrapy

# объявим свойства, которые будут хранить собранные данные
class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    salary_cur = scrapy.Field()
    salary = scrapy.Field()
    company = scrapy.Field()
    salary_conditions = scrapy.Field()
    url = scrapy.Field()
    location = scrapy.Field()
    _id = scrapy.Field()

