import scrapy
from scrapy.http import HtmlResponse
from castorama_parser.items import CastoramaParserItem
from scrapy.loader import ItemLoader


class CastoramaruSpider(scrapy.Spider):
    name = "castoramaru"
    allowed_domains = ["castorama.ru"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.start_urls = [f"https://www.castorama.ru/catalogsearch/result/?q={kwargs.get('query')}&PAGEN_3={self.page}"]

    def parse(self, response: HtmlResponse):

        # ссылки с текущей страницы сайта
        links = response.xpath('//a[@class="product-card__img-link"]')
        if links:
            for link in links:
                yield response.follow(link, callback=self.parse_castorama)

        # переход на следующую страницу сайта
        next_page = response.xpath("//a[@title='След.']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_castorama(self, response: HtmlResponse):

        loader = ItemLoader(item=CastoramaParserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@class="price"]//text()')
        loader.add_xpath('product_code', '//div[@class="product-essential__sku"]//text()')
        loader.add_xpath('photos', '//div[@class="js-zoom-container"]/img[@src][1]/@data-src')
        loader.add_value('url', response.url)
        yield loader.load_item()

        # name = response.xpath("//h1/text()").get().strip()
        # price = int(response.xpath("//span[@class='price']//text()").getall()[2].replace(' ', ''))
        # product_code = response.xpath("//div[@class='product-essential__sku']//text()").getall()[1]
        # photos = response.xpath("//div[@class='js-zoom-container']/img[@src][1]/@data-src").getall()
        # photos = ["https://www.castorama.ru" + photo for photo in photos]
        # url = response.url
        #
        # yield CastoramaParserItem(name=name, price=price, product_code=product_code, photos=photos, url=url)

