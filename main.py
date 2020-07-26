from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito_parse.avito_parse import settings
from avito import AvitoSpider

if __name__ == '__main__':
    crawl_proc = CrawlerProcess(settings=Settings().setmodule(settings))
    crawl_proc.crawl(AvitoSpider)
    crawl_proc.start()
