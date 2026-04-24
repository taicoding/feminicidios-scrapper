# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScraperItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    tag = scrapy.Field()
    section = scrapy.Field()
    source = scrapy.Field()
    published_at = scrapy.Field()
