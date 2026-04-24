# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from datetime import datetime
from mongoengine.errors import ValidationError, NotUniqueError
from models.news import News
from utils.database import initialize_database


class NewsScraperPipeline:
    def __init__(self):
        self.items_processed = 0

    def open_spider(self, spider):
        try:
            initialize_database()
            logging.info("Database connection established successfully.")
        except Exception as e:
            spider.logger.error(f"Failed to connect to the database: {e}")

    def process_item(self, item, spider):
        try:
            News.objects(url=item["url"]).update_one(
                set_on_insert__title=item["title"],
                set_on_insert__body=item["body"],
                set_on_insert__tag=item.get("tags"),
                set_on_insert__source=item["source"],
                set_on_insert__section=item["section"],
                set_on_insert__published_at=item["published_at"],
                set_on_insert__created_at=datetime.now(),
                upsert=True,
            )
            self.items_processed += 1
            spider.logger.debug(f"Item processed successfully: {item['url']}")
        except ValidationError as ve:
            spider.logger.warning(f"Validation error for item {item['url']}: {ve}")
        except NotUniqueError as nue:
            spider.logger.warning(f"Duplicate item skipped: {item['url']} - {nue}")
        except Exception as e:
            spider.logger.error(f"Error processing item {item['url']}: {e}")
        return item

    def close_spider(self, spider):
        spider.logger.info(
            f"Spider closed. Total items processed: {self.items_processed}"
        )
