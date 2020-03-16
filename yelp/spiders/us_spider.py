import scrapy


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    start_urls = [
        'https://www.yelp.com/biz/nespresso-boutique-new-york-6'
    ]

    def parse(self, response):
        name = response.css("h1::text").get()

        categories = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/span[2]/span/a/text()"""
        ).extract()
        category = " > ".join(categories)

        phone = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[2]/div/div/section[2]/div/div[2]/div/div[2]/p[2]/text()"""
        ).get()

        yield {
            'name': name,
            'category': category,
            'phone': phone,
        }




