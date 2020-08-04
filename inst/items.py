# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst

def unix(values):
    values = datetime.datetime.fromtimestamp(values).strftime("%H:%M:%S %d-%m-%Y")
    return values

class InstItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    user_name = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    post_photos = scrapy.Field()
    post_pub_date = scrapy.Field(input_processor=MapCompose(unix), output_processor=TakeFirst())
    like_count = scrapy.Field(output_processor=TakeFirst())
