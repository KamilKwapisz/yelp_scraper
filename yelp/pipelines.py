from scrapy.exceptions import DropItem


class YelpPipeline(object):

    def open_spider(self, spider):
        self.scraped_names = set()

    def process_item(self, item, spider):
        if item['name'] in self.scraped_names:
            raise DropItem(f"Duplicated comapny name: {item['name']}")
        else:
            self.scraped_names.add(item['name'])
            return item
