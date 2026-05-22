import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem

CURL_META = {"playwright": True}


class EldiarioSpider(scrapy.Spider):
    name = "eldiario"
    allowed_domains = ["www.eldiario.net"]
    start_urls = [
        f"https://www.eldiario.net/portal/page/{i}/?s=feminicidio" for i in range(1, 3)
    ]
    allowed_sections = set(["seguridad", "nacional"])

    def date_formatter(self, date_str, date_format="%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, date_format)
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            return None

    def tag_formatter(self, tags):
        try:
            list_tags = [t.lower().strip() for t in tags.split("-")]
            return list_tags
        except Exception as e:
            self.logger.error(f"Error formatting tags: {e}")
            return tags

    def section_formatter(self, tags):
        try:
            return tags[1] if len(tags) > 1 else tags[0]
        except Exception as e:
            self.logger.error(f"Error formatting section: {e}")
            return None

    def check_category(self, category):
        print(category, self.allowed_sections)
        print(set(category.lower().split(" - ")))
        if not category:
            return False
        return self.allowed_sections.intersection(set(category.lower().split(" - ")))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta=CURL_META)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_xpaths="//h3[contains(@class, 'entry-title')]/a"
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Found {len(links)} valid links")

        for link in links:
            yield scrapy.Request(
                url=link.url, callback=self.parse_article, meta=CURL_META
            )

    def parse_article(self, response):
        category = response.css("a.tdb-entry-category::text").get()
        if self.check_category(category):
            loader = ItemLoader(item=NewsItem(), response=response)
            loader.add_value("url", response.url)
            loader.add_css("title", "h1.tdb-title-text::text")
            body = [
                p.xpath("string(.)").get()
                for p in response.xpath(
                    "//div[contains(@class, 'td-post-content')]/div[contains(@class, 'td-fix-index')]/p"
                )
            ]
            loader.add_value("body", body)
            tags = self.tag_formatter(category)
            loader.add_value("tags", tags)
            section = self.section_formatter(tags)
            loader.add_value("section", section)

            published_at = response.css("time.td-module-date::text").get()
            if published_at:
                loader.add_value("published_at", self.date_formatter(published_at))
            else:
                self.logger.warning(
                    f"Not possible to extract published_at for {response.url}"
                )
            loader.add_value("source", self.name)

            yield loader.load_item()

        self.logger.info(
            "Noticia descartada por sección no relacionada con seguridad: "
            f"{response.url}"
        )
        return
