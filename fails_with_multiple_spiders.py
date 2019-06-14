import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import Request, signals
from scrapy.exceptions import DontCloseSpider
from scrapy.xlib.pydispatch import dispatcher


class SpideIdleTest(scrapy.Spider):
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def __init__(self):
        dispatcher.connect(self.spider_idle, signals.spider_idle)
        self.idle_retries = 0

    def spider_idle(self, spider):
        self.idle_retries += 1
        if self.idle_retries < 3:
            self.crawler.engine.crawl(
                Request('https://www.google.com',
                        self.parse,
                        dont_filter=True),
                spider)
            raise DontCloseSpider("Stayin' alive")

    def start_requests(self):
        yield Request('https://www.google.com', self.parse)

    def parse(self, response):
        print(response.css('title::text').extract_first())


process = CrawlerProcess()
process.crawl(SpideIdleTest)
process.crawl(SpideIdleTest)
process.crawl(SpideIdleTest)
process.start()