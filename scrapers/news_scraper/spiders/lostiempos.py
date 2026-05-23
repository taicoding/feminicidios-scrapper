import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem


class LostiemposSpider(scrapy.Spider):
    name = "lostiempos"
    allowed_domains = ["www.lostiempos.com"]
    start_urls = [
        f"https://www.lostiempos.com/etiqueta/feminicidio?page={i}" for i in range(0, 3)
    ]
    deny_section = [
        "/tendencias/",
        "/mundo/",
        "/tendencias/",
        "/opinion/",
        "/politico/",
        "/economia/",
    ]

    def date_formatter(self, url, date_format="%Y%m%d"):
        try:
            url_split = url.split("/")
            date_str = url_split[5]
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
            self.logger.error(f"Error formatting section: {e} at URL: {url}")
            return None

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_xpaths='(//div[@class="view-content"])[1]//div[contains(@class, "views-field-title")]',
            deny=self.deny_section,
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Found {len(links)} valid links")

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse_article)

    def parse_article(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css("title", "h1.node-title::text")
        loader.add_css("body", "div.body p::text")
        loader.add_css("tags", "ul.field-items li a::text")
        loader.add_value("source", self.name)
        section = self.section_formatter(response.url)
        if section:
            loader.add_value("section", section)
        else:
            self.logger.warning(f"Not possible to extract section for {response.url}")
        published_at = self.date_formatter(response.url)
        if published_at:
            loader.add_value("published_at", published_at)
        else:
            self.logger.warning(
                f"Not possible to extract published_at for {response.url}"
            )
        yield loader.load_item()
