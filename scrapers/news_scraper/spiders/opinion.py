import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem


class OpinionSpider(scrapy.Spider):
    name = "opinion"
    allowed_domains = ["www.opinion.com.bo"]
    start_urls = [
        f"https://www.opinion.com.bo/tags/feminicidio?page={i}" for i in range(1, 3)
    ]

    deny_section = [
        "/escenario-politico1/",
        "/revista-asi/",
        "/deportes/",
        "/cultura/",
        "/pais/",
        "/mundo/",
        "/video/",
        "/ramona/",
        "/tendencias/",
    ]

    def date_formatter(self, url, date_format="%Y%m%d"):
        try:
            url_split = url.split("/")
            date_str = url_split[6][:8]
            date_publish = datetime.strptime(date_str, date_format)
            return date_publish
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            return None

    def section_formatter(self, url):
        try:
            url_split = url.split("/")
            section = url_split[4]
            return section
        except Exception as e:
            self.logger.error(f"Error al formatear sección: {e}")
            return url
