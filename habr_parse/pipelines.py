# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from habr_parse.items import HabrAutorParseItem, HabrPostParseItem

class HabrParsePipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['habr']

    def process_item(self, item, spider):
        if isinstance(item, HabrPostParseItem):
            collection = self.db['Posts']
            collection.insert_one(item)
        elif isinstance(item, HabrAutorParseItem):
            collection = self.db['Autors']
            collection.insert_one(item)
        return item
