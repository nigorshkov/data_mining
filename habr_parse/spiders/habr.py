import scrapy
from habr_parse.items import HabrPostParseItem, HabrAutorParseItem
from scrapy.loader import ItemLoader

class HabrSpider(scrapy.Spider):
    name = 'habr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/']

    xpath = {
        'pagination': '//li[@class = "toggle-menu__item toggle-menu__item_pagination"]/a/@href',
        'post': '//h2[@class = "post__title"]/a/@href',
        'title': '//span[@class = "post__title-text"]/text()',
        'images': '//div[@id = "post-content-body"]/img/@src',
        'comments': '//span[@id = "comments_count"]/text()',
        'autor_name': '//header[@class = "post__meta"]/a/span/text()',
        'autor_url': '//header[@class = "post__meta"]/a/@href',
        'information': '//ul[@class = "defination-list"]',
        'name': '//a[@class = "user-info__fullname user-info__fullname_medium"]/text()',
        'nickname': '//a[@class = "user-info__nickname user-info__nickname_doggy"]/text()',
        'contact_info': '//ul[@class = "profile-page__links defination-list"]',
        'autor_post_url': '//a[@class = "tabs-menu__item tabs-menu__item_link"]/@href'
    }

    def parse(self, response):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.parse)

        for post_url in response.xpath(self.xpath['post']):
            yield response.follow(post_url, callback=self.post_parse)

    def post_parse(self, response):
        item = ItemLoader(HabrPostParseItem(), response)
        item.add_xpath('title', self.xpath['title'])
        item.add_xpath('images', self.xpath['images'])
        item.add_xpath('comments', self.xpath['comments'])
        item.add_xpath('autor_name', self.xpath['autor_name'])
        item.add_xpath('autor_url', self.xpath['autor_url'])
        item.add_value('post_url', response.url)

        yield item.load_item()

        for autor_url in response.xpath(self.xpath['autor_url']):
            yield response.follow(autor_url, callback=self.autor_parse)

    def autor_parse(self, response):
        item = ItemLoader(HabrAutorParseItem(), response)
        item.add_xpath('information', self.xpath['information'])
        item.add_xpath('name', self.xpath['name'])
        item.add_value('url', response.url)
        item.add_xpath('nickname', self.xpath['nickname'])
        item.add_xpath('contact_info', self.xpath['contact_info'])

        yield item.load_item()

        yield response.follow(response.xpath(self.xpath['autor_post_url'])[1].extract(), callback=self.parse)
