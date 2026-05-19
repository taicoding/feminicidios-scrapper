import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem


class ElpaisSpider(scrapy.Spider):
    name = "elpais"
    allowed_domains = ["elpais.bo"]
    start_urls = [
        f"https://elpais.bo/tags/view/Feminicidio?page={i}" for i in range(1, 3)
    ]
    deny_section = [
        "/reportajes/",
        "/multimedia/",
        "/gobernacion-tarija/",
        "/opinion/",
        "/alcaldia-tarija/",
        "/economia/",
        "/internacional/",
        "/sociales/",
    ]

    def date_formatter(self, url, date_format="%Y%m%d"):
        try:
            url_split = url.split("/")
            date_str = url_split[4][:8]
            date_publish = datetime.strptime(date_str, date_format)
            return date_publish
        except Exception as e:
            self.logger.error(f"Error al formatear fecha: {e}")
            return None

    def section_formatter(self, url):
        try:
            url_split = url.split("/")
            section = url_split[3]
            return section
        except Exception as e:
            self.logger.error(f"Error al formatear sección: {e}")
            return url

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_xpaths="(//ul[contains(@class,'uk-switcher')]//li)[1]//a[@class='link-news']",
            deny=self.deny_section,
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Se encontraron {len(links)} enlaces válidos")

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse_article)

    def parse_article(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css("title", "h1.ep_post_title::text")
        loader.add_value(
            "body", response.css("div.note-body p").xpath("string()").getall()
        )
        loader.add_css("tags", "ul.uk-subnav li a::text")
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
