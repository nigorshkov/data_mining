# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from avito_parse.avito_parse import settings

class AvitoParsePipeline:
    def process_item(self, item, spider):
        return item

class Mongo(object):

    def __init__(self):
        connection = pymongo.MongoClient(

            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]

        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item):
        self.collection.insert(dict(item))
        return item