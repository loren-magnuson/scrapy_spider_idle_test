from scrapy import Request, signals, Spider
from scrapy.exceptions import DontCloseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from billiard import Process

from scrapy.crawler import CrawlerProcess


class SpiderIdleTest(Spider):

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'LOG_LEVEL': 'DEBUG'
    }

    def __init__(self):
        dispatcher.connect(self.spider_idle, signals.spider_idle)
        self.idle_retries = 0

    def spider_idle(self, spider):
        self.idle_retries += 1
        if self.idle_retries < 3:
            spider.crawler.engine.crawl(
                Request('https://www.google.com',
                        self.parse,
                        dont_filter=True),
                spider)
            raise DontCloseSpider("Stayin' alive")

    def start_requests(self):
        yield Request('https://www.google.com', self.parse)

    def parse(self, response):
        print(response.css('title::text').extract_first())


class CrawlerScript(Process):

    def __init__(self, spider):
        Process.__init__(self)
        self.spider = spider

    def run(self):
        process = CrawlerProcess()
        process.crawl(SpiderIdleTest)
        process.start()


def crawl_async():
    spider = SpiderIdleTest()
    crawler = CrawlerScript(spider)
    crawler.start()


for i in range(0, 2):
    from time import sleep
    sleep(5)
    crawl_async()
