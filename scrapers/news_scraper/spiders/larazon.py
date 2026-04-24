import scrapy


class LarazonSpider(scrapy.Spider):
    name = "larazon"
    allowed_domains = ["www.la-razon.com"]
    start_urls = ["https://www.la-razon.com"]

    def parse(self, response):
        pass
