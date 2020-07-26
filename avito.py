import scrapy
from avito_parse.avito_parse.items import AvitoParseItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ?p1&cd=1']
    xpath_sel = {
        'pagination': '//a[@class = "pagination-page"]/@href',
        'ad': '//div[@class = "snippet-title-row"]//a[@class = "snippet-link"]/@href'
    }

    ad_template = {
        'title': '//span[@class = "title-info-title-text"]/text()',
        'url': '//link[@rel = "canonical"]/@href',
        'cost': '//div[@class = "item-price"]//span[@itemprop = "price"]/text()'
    }

    def parse(self, response):
        pagination = response.xpath(self.xpath_sel['pagination'])
        for url in pagination:
            yield response.follow(url, callback=self.parse)

        ad_url = response.xpath(self.xpath_sel['ad'])
        for ad in ad_url:
            yield response.follow(ad, callback=self.ad_parse)

    def ad_parse(self, response):
        item = AvitoParseItem()
        for key, value in self.ad_template.items():
            item[key] = response.xpath(value).extract_first()
        item['chars'] = [{'name': char.xpath('span/text()').extract_first(), 'value': char.xpath('text()').extract()}
                         for char in response.xpath('//ul[@class = "item-params-list"]/li')]
        yield item
