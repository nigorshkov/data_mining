# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def comments(values):
    str = ''
    for i in values:
        if i != ' ' and i != '\n':
            str += i
    values = str
    return values

def information(values):
    info = []
    for i in range(values.count('<li ')):
        dict = {}
        start = values.find('label_profile-summary">')
        end = values.find('</span>')
        dict['name'] = values[start+23:end]
        values = values[end+7:]
        start = values.find('defination-list__value">')
        if values.find('defination-list__link">') < 150:
            start = values.find('defination-list__link">')
        end = values.find('</')
        dict['value'] = values[start+24:end]
        end = values.find('</li>')
        values = values[end+5:]
        info.append(dict)
    return info

def contact_info(values):
    contact_info_list = []
    for i in range(values.count('<li ')):
        dict = {}
        start = values.find('defination-list__label_profile-links">')
        end = values.find('</span>')
        dict['name'] = values[start+38:end]
        values = values[end+7:]
        start = values.find('class="url icon">')
        if start == -1:
            start = values.find('class="url">')
            values = values[start+12:]
        else:
            values = values[start+17:]
        end = values.find('</')
        dict['value'] = values[0:end]
        end = values.find('</li>')
        values = values[end+5:]
        contact_info_list.append(dict)
    return contact_info_list

class HabrPostParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
    comments = scrapy.Field(input_processor=MapCompose(comments), output_processor=TakeFirst())
    autor_name = scrapy.Field(output_processor=TakeFirst())
    autor_url = scrapy.Field(output_processor=TakeFirst())
    post_url = scrapy.Field(output_processor=TakeFirst())

class HabrAutorParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    information = scrapy.Field(input_processor=MapCompose(information))
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    nickname = scrapy.Field(output_processor=TakeFirst())
    contact_info = scrapy.Field(input_processor=MapCompose(contact_info))
