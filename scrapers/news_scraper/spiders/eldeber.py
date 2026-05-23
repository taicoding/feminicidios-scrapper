import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem


class EldeberSpider(scrapy.Spider):
    name = "eldeber"
    allowed_domains = ["eldeber.com.bo"]
    start_urls = [f"https://eldeber.com.bo/tag/feminicidio/{i}/" for i in range(1, 3)]
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
        "/rfi/",
    ]

    def date_formatter(self, date_str, date_format="%Y-%m-%d"):
        try:
            date_publish = date_str.split(" ")[0]
            return datetime.strptime(date_publish, date_format)
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            return None

    def section_formatter(self, url):
        try:
            url_split = url.split("/")
            section = url_split[3]
            return section
        except Exception as e:
            self.logger.error(f"Error formatting section: {e} at URL: {url}")
            return None

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_css="h2.nota__titulo-item a",
            deny=self.deny_section,
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Found {len(links)} valid links")

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse_article)

    def parse_article(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css("title", "h1.articulo__titulo::text")
        loader.add_value(
            "body", response.css("main.articulo__cuerpo > p").xpath("string()").getall()
        )
        loader.add_css("tags", "a.tags__link::text")
        loader.add_value("source", self.name)
        section = self.section_formatter(response.url)
        if section:
            loader.add_value("section", section)
        else:
            self.logger.warning(f"Not possible to extract section for {response.url}")
        published_at = response.css("input.datos_ubicacion::attr(data-fecha_c)").get()
        if published_at:
            loader.add_value("published_at", self.date_formatter(published_at))
        else:
            self.logger.warning(
                f"Not possible to extract published_at for {response.url}"
            )
        yield loader.load_item()
