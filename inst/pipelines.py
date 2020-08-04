# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class InstPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['Inst']

    def process_item(self, item, spider):
        collection = self.db['Posts']
        collection.insert_one(item)
        return item


class ImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('post_photos', []):
            try:
                yield Request(url)
            except ValueError as e:
                print(e)

    def item_completed(self, results, item, info):
        item['post_photos'] = [itm[1] for itm in results]
        return item
