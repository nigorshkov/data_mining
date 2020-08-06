# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class ZillowParsePipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['Zillow']

    def process_item(self, item, spider):
        collection = self.db['ad']
        collection.insert_one(item)
        return item

class ImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('photos', []):
            try:
                yield Request(url)
            except ValueError as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results]
        return item
