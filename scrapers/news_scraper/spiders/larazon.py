import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from ..items import NewsScraperItem as NewsItem

CURL_META = {"curl_cffi_options": {"impersonate": "chrome110"}}


class LarazonSpider(scrapy.Spider):
    name = "larazon"
    allowed_domains = ["larazon.bo"]
    start_urls = start_urls = [
        f"https://larazon.bo/tags/feminicidio/page/{i}" for i in range(1, 4)
    ]
    deny_section = [
        r"/lr-article/",
        r"/mundo/",
        r"/voces/",
        r"/opinion/",
        r"/la-revista/",
        r"/politico/",
        r"/marcas/",
        r"/economia/",
    ]

    def date_formatter(self, url, date_format="%Y%m%d"):
        try:
            url_split = url.split("/")
            date_str = url_split[4] + url_split[5] + url_split[6]
            date_publish = datetime.strptime(date_str, date_format)
            return date_publish
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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta=CURL_META)

    def parse(self, response):
        extractor = LinkExtractor(
            restrict_css="article.jeg_post.jeg_pl_md_2.format-standard h3.jeg_post_title",
            deny=self.deny_section,
        )
        links = extractor.extract_links(response)
        self.logger.info(f"Se encontraron {len(links)} enlaces válidos")

        for link in links:
            yield scrapy.Request(
                url=link.url, callback=self.parse_article, meta=CURL_META
            )

    def parse_article(self, response):
        loader = ItemLoader(item=NewsItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_css("title", "div.entry-header h1::text")
        loader.add_css("body", "div.content-inner p::text")
        loader.add_css("tags", "div.jeg_post_tags a::text")
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
