# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest, CloseSpider
import logging

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from models.news import News
from utils.database import initialize_database


class NewsScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class NewsScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.duplicates_count = 0
        self.duplicate_threshold = 10
        self.logger = logging.getLogger(self.__class__.__name__)
        self.spider_closed = False

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        try:
            initialize_database()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database connection: {e}")
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # If CloseSpider was already raised, ignore pending requests
        if self.spider_closed:
            raise IgnoreRequest("Spider already closing due to duplicate threshold")

        # Check if URL already exists in MongoDB
        if self._is_duplicate(request.url, spider):
            self.duplicates_count += 1
            spider.logger.warning(
                f"[DUPLICATE] URL already in database: {request.url} "
                f"({self.duplicates_count}/{self.duplicate_threshold})"
            )

            # If threshold is reached, close the spider (only once)
            if self.duplicates_count >= self.duplicate_threshold:
                self.spider_closed = True  # Mark as closed
                spider.logger.info(
                    f"Duplicate URL threshold reached ({self.duplicate_threshold}). "
                    "Closing spider..."
                )
                raise CloseSpider(reason="duplicate_url_threshold_reached")

            # Ignore this request without making HTTP call
            raise IgnoreRequest(f"URL already in database: {request.url}")

        # Reset counter when a new URL is found
        self.duplicates_count = 0
        return None

    def _is_duplicate(self, url, spider):
        """
        Checks if URL already exists in MongoDB database.
        Returns True if exists (is duplicate), False otherwise.
        """
        try:
            exists = News.objects(url=url).first()
            return exists is not None
        except Exception as e:
            spider.logger.error(f"Error checking duplicate in database: {e}")
            return False

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
