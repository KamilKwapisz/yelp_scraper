import scrapy


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    start_urls = [
        'https://www.yelp.com/biz/nespresso-boutique-new-york-6'
    ]

    def parse(self, response):
        pass
