import scrapy
from zillow_parse.items import ZillowParseItem
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['http://www.zillow.com/']
    browser = webdriver.Firefox()
    xpath = {'pagination': '//nav[@role="navigation"]/ul/li/a/@href',
             'ad': '//div[@id="grid-search-results"]/ul/li/article/div[@class="list-card-info"]/a/@href',
             'price': '//div[@class="ds-chip"]//span[@class="ds-value"]/text()',
             'address': '//div[@class="ds-chip"]//h1[@class="ds-address-container"]',
             'media': '//div[@class="ds-media-col ds-media-col-hidden-mobile"]',
             'photos': '//div[@class="ds-media-col ds-media-col-hidden-mobile"]'
                       '/ul/li/button/picture/source[@type="image/jpeg"]'}

    def __init__(self, location: list, *args, **kwargs):
        self.location = location
        super().__init__(*args, **kwargs)

    def parse(self, response):
        # Перебор по названиям
        # self.browser.get(self.start_urls[0])
        # for loc in self.location:
        #     input_loc = self.browser.find_element_by_xpath('//input[contains(@id, "search-box-input")]')
        #     input_loc.send_keys(loc)
        #     sleep(5)
        #     input_loc.send_keys(Keys.ENTER)
        #     sleep(5)
        #     button = self.browser.find_element_by_xpath('//button[@class = "sc-14dvu6m-4 fHnlHd "]')
        #     button.click()
        #     yield response.follow(self.browser.current_url, callback=self.page_parse)
        # Обходим список городов
        for loc in self.location:
            yield response.follow(self.start_urls[0]+loc, callback=self.loc_parse)

    def loc_parse(self, response):
        for pag_url in response.xpath(self.xpath['pagination']):
            yield response.follow(pag_url, callback=self.loc_parse)

        for ad_url in response.xpath(self.xpath['ad']):
            yield response.follow(ad_url, callback=self.ad_parse)

    def ad_parse(self, response):
        self.browser.get(response.url)
        item = ItemLoader(ZillowParseItem(), response)
        item.add_xpath('price', self.xpath['price'])
        item.add_xpath('address', self.xpath['address'])
        media = self.browser.find_element_by_xpath(self.xpath['media'])
        len_media = self.browser.find_elements_by_xpath(self.xpath['photos'])
        while True:
            media.send_keys(Keys.PAGE_DOWN)
            sleep(1)
            media.send_keys(Keys.PAGE_DOWN)
            sleep(1)
            tmp_len = self.browser.find_elements_by_xpath(self.xpath['photos'])
            if len_media == tmp_len:
                break
            len_media = tmp_len
        item.add_xpath('photos', self.xpath['photos'])
        yield item.load_item()
