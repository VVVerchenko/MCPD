import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import hashlib

class HhruSpider(scrapy.Spider):
    name = "hhru"
    # указываем сайты к которым будет доступ через запятую
    allowed_domains = ["hh.ru"]
    # точка входа на сайт, можно указать несколько точек входа с разными параметрами через запятую, будут обрабатываться параллельно
    # start_urls = ["https://chelyabinsk.hh.ru/search/vacancy?text=data+scientist&salary=&area=1&ored_clusters=true",
    #               "https://chelyabinsk.hh.ru/search/vacancy?text=data+scientist&salary=&area=2&ored_clusters=true"]
    start_urls = ["https://chelyabinsk.hh.ru/search/vacancy?text=data+scientist&salary=&area=1&ored_clusters=true&items_on_page=20",
                  "https://chelyabinsk.hh.ru/search/vacancy?text=data+scientist&salary=&area=2&ored_clusters=true&items_on_page=20"]



    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='serp-item__title']/@href").getall()
        for link in links:
            # для многократного возврата результата вместо return используем yield
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # пропишем селекторы и соберём данные по каждой вакансии
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//div[@data-qa='vacancy-salary']/span//text()").getall()
        location = response.xpath('//p[@data-qa="vacancy-view-location"]//text()').extract()
        company = response.xpath('//span[@class="vacancy-company-name"]//text()').getall()
        url = response.url
        _id = response.url.split('/')[-1].split('?')[0]  # извлечь только номер вакансии из URL-адреса
        _id = hashlib.md5(_id.encode()).hexdigest()  # создать хэш от номера вакансии
        yield JobparserItem(name=name, salary=salary, location=location, company=company, url=url, _id=_id)

        print()

