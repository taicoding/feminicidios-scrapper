import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem


class EldeberSpider(scrapy.Spider):
    name = "eldeber"
    allowed_domains = ["eldeber.com.bo"]
    start_urls = [f"https://eldeber.com.bo/tag/feminicidio/{i}/" for i in range(1,3)"]
    deny_section = [
        "/mundo/",
        "/opinion/",
        "/bbc/",
        "/tendencias/",
        "/economia/",
        "/escenas/",
        "/politica/",
        "/noticias/",
        "/para-ellas/",
        "/coronavirus/",
        "/dw/",
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_css="h2.nota__titulo-item a",
            deny=self.deny_section,
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Se encontraron {len(links)} enlaces válidos")

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse_article)

    def parse_article(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css("title", "h1.articulo__titulo::text")
        loader.add_value(
            "body", response.css("div.articulo__body p").xpath("string()").getall()
        )
        loader.add_css("tags", "a.tags__link::text")
        loader.add_value("source", self.name)
        