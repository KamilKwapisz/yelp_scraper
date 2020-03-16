import scrapy

from yelp.items import ProfileItem, ReviewItem


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    start_urls = [
        'https://www.yelp.com/biz/nespresso-boutique-new-york-6'
    ]

    def parse(self, response):
        profile_item = ProfileItem()
        name = response.css("h1::text").get()

        categories = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/span[2]/span/a/text()"""
        ).extract()
        category = " > ".join(categories)

        phone = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[2]/div/div/section[2]/div/div[2]/div/div[2]/p[2]/text()"""
        ).get()

        profile_item['name'] = name
        profile_item['category'] = category
        profile_item['phone'] = phone

        reviews = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[3]/section[2]/div[2]/div"""
        ).css("div[aria-label*='rating']")

        review_items = list()

        for review in reviews:
            rating = review.xpath('@aria-label').get().split(' ')[0]
            review_item = ReviewItem()
            review_item['rating'] = int(rating)
            review_items.append(dict(review_item))

        profile_item['reviews'] = review_items

        yield profile_item





