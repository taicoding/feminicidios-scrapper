# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from datetime import datetime
from mongoengine.errors import ValidationError, NotUniqueError
from scrapy.exceptions import CloseSpider
from models.news import News
from utils.database import initialize_database


class NewsScraperPipeline:
    def __init__(self):
        self.items_processed = 0
        self.duplicates_in_pipeline = 0

    def open_spider(self, spider):
        try:
            initialize_database()
            logging.info("Database connection established successfully.")
        except Exception as e:
            spider.logger.error(f"Failed to connect to the database: {e}")

    def process_item(self, item, spider):
        try:
            # Double check (redundancy just in case)
            exists = News.objects(url=item["url"]).first()
            if exists:
                self.duplicates_in_pipeline += 1
                spider.logger.debug(f"Duplicate caught in pipeline: {item['url']}")
                return item

            news = News(
                url=item["url"],
                title=item["title"],
                body=item["body"],
                tags=item["tags"],
                source=item["source"],
                section=item["section"],
                published_at=item["published_at"],
            )
            news.save()
            self.items_processed += 1
            spider.logger.info(f"✓ Item saved: {item['title'][:50]}...")

        except ValidationError as ve:
            spider.logger.warning(f"Validation error for item {item['url']}: {ve}")
        except Exception as e:
            spider.logger.error(f"Error processing item {item['url']}: {e}")

        return item

    def close_spider(self, spider):
        spider.logger.info(
            f"Spider closed. Items saved: {self.items_processed}, "
            f"duplicates in pipeline: {self.duplicates_in_pipeline}"
        )
