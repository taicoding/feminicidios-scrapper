# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from datetime import datetime


def clean_title(title):
    if title:
        return title.replace("“", '"').replace("”", '"').strip()
    return title


def clean_body_text(text):
    # Combinación de tu body_formatter y caracteres especiales
    if text:
        cleaned = (
            text.strip()
            .replace("\xa0", " ")
            .replace('"', "")
            .replace("\ufeff", " ")
            .replace("“", '"')
            .replace("”", '"')
            .replace("\u200b", " ")
        )
        return cleaned if cleaned not in [" ", ""] else None
    return None


def format_tags(tag):
    if tag:
        return tag.lower().strip()
    return tag


class NewsScraperItem(scrapy.Item):
    url = scrapy.Field(
        input_processor=MapCompose(clean_title), output_processor=TakeFirst()
    )
    title = scrapy.Field(output_processor=TakeFirst())
    body = scrapy.Field(input_processor=MapCompose(clean_body_text))
    tags = scrapy.Field(input_processor=MapCompose(format_tags))
    section = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=TakeFirst())
    published_at = scrapy.Field(output_processor=TakeFirst())
