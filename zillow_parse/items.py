# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def address(values):
    value = ''
    while True:
        start = values.find('<span>')
        end = values.find('</span>')
        if end == -1:
            break
        value += values[start + 6:end]
        values = values[end + 7:]
    return value.replace('<!-- -->', '')


def photo(values):
    values = values[values.find('"h') + 1:values.find('w"')]
    lst = values.split(', ')
    value = lst[len(lst) - 1]
    value = value[:value.find(' ')]
    return value


class ZillowParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    price = scrapy.Field(output_processor=TakeFirst())
    address = scrapy.Field(input_processor=MapCompose(address), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(photo))
