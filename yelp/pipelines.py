from scrapy.exceptions import DropItem
import json


class DuplicationDetectorPipeline(object):

    def process_item(self, item, spider):
        if spider.parsing_profile_page is False:  # we are scraping from a list
            try:
                with open('items.json', 'r') as json_file:
                    scraped_profiles = json.loads(json_file.read())
                    names = [profile['name'] for profile in scraped_profiles]
                    if item['name'] in names:
                        raise DropItem(f"Duplicated company name: {item['name']}")
            except (FileNotFoundError, json.JSONDecodeError, TypeError):  # no items collected yet
                pass  # item can be saved by far
        return item


class YelpPipeline(object):

    def open_spider(self, spider):
        self.scraped_names = set()

    def process_item(self, item, spider):
        if item['name'] in self.scraped_names:
            raise DropItem(f"Duplicated comapny name: {item['name']}")
        else:
            self.scraped_names.add(item['name'])
            return item


class WriterPipeline(object):

    def open_spider(self, spider):
        if spider.parsing_profile_page:
            self.file = open('item.json', 'a')
        else:
            self.file = open('items.json', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
