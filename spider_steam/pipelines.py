# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from itemadapter import ItemAdapter
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SpiderSteamPipeline:
    def open_spider(self, spider):
        self.file = open('items.json', 'w')

    def close_spider(self, spider): 
        self.file.close()

    def process_item(self, item, spider):
        if item['release_date'][-4:] <= '2000':
            return 
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item
