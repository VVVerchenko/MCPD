import scrapy
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader

class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.query = kwargs.get('query')
        self.start_urls = [f"https://www.avito.ru/chelyabinsk/{self.query}?p={self.page}"]

    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield SplashRequest(url)

    def parse(self, response):
        # определим максимальный номер страницы
        max_num_page = int(max(response.xpath("//span[@class='styles-module-text-InivV']//text()").getall(), key=int))
        # соберём ссылки с текущей страницы
        links = response.xpath("//a[@data-marker='item-title']/@href").getall()
        if links:
            for link in links:
                yield SplashRequest("https://www.avito.ru" + link, callback= self.parse_ads)

        # переход на следующую страницу сайта
        # next_page = response.xpath("//a[@data-marker='pagination-button/nextPage']")
        if self.page < max_num_page:
            self.page += 1
            yield SplashRequest(response.url, callback=self.parse, args={'query': f'p={self.page}'}, dont_filter=True)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_xpath('name', "//span[@class='title-info-title-text']//text()")
        loader.add_xpath('seller', "//div[@data-marker='seller-info/name']//text()")
        loader.add_xpath('price', "//span[@itemprop='price']//text()")
        loader.add_xpath('currency', "//span[@itemprop='priceCurrency']//text()")
        loader.add_xpath('photos', "//div[contains(@class,'image-frame-borderWrapper')]//@src")
        loader.add_value('url', response.url)
        yield loader.load_item()


# name = response.xpath("//span[@class='title-info-title-text']//text()").get()
# seller = response.xpath("//div[@data-marker='seller-info/name']//text()").get()
# price = int(response.xpath("//span[@itemprop='price']//text()").get().replace('\xa0', ''))
# currency = response.xpath("//span[@itemprop='priceCurrency']//text()").get().replace('\xa0', '')
# loader.add_xpath('photos', 'response.xpath("//div[contains(@class,"image-frame-borderWrapper")]//@src").get()')
# url = response.url
# yield AvitoparserItem(name=name, seller=seller, price=price, currency=currency, url=url)
