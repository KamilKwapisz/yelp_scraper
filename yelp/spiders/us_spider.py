import scrapy
from scrapy.exceptions import CloseSpider
import pendulum

from yelp.items import ProfileItem, ReviewItem


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    number = 20
    page = 1
    max_page_number = None
    start_urls = [
        "https://www.yelp.com/biz/nespresso-boutique-new-york-6?start=0"
    ]
    profile_item = None
    profile_crawler = True

    def __init__(self, profile_url=None, list_url=None, *args, **kwargs):
        super(SpiderUS, self).__init__(*args, **kwargs)
        if profile_url:
            self.start_urls = [profile_url]
        elif list_url:
            self.profile_crawler = False
        else:
            # raise CloseSpider('ivalid_argument')
            pass
            
    def change_date_format(self, date):
        dt = pendulum.from_format(date, 'M/D/YYYY')
        return dt.to_date_string()

    def start_requests(self):
        if self.profile_crawler:
            yield scrapy.Request(self.start_urls[0], self.parse_profile)
    
    def parse_profile(self, response):
        self.profile_item = ProfileItem()
        name = response.css("h1::text").get()

        categories = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/span[2]/span/a/text()"""
        ).getall()
        category = " > ".join(categories)

        phone = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[2]/div/div/section[2]/div/div[2]/div/div[2]/p[2]/text()"""
        ).get(None)

        street = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/address/p[1]/span/text()"""
        ).get()

        city = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/address/p[2]/span/text()"""
        ).get(None)

        addr = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/div/p[1]/text()"""
        ).get(None)

        addr2 = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/div/p[2]/text()"""
        ).get(None)

        address = f"{street}, {city}, {addr}, {addr2}"

        city_name = city.split(', ')[0]

        self.profile_item['name'] = name
        self.profile_item['category'] = category
        self.profile_item['phone'] = phone
        self.profile_item['city'] = city_name
        self.profile_item['address'] = address

        pagination = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[3]/section[2]/div[2]/div/div[4]/div[1]/span/text()"""
        ).get(None)

        self.max_page_number = pagination.split(" ")[-1]
        
        next_url = f"https://www.yelp.com/biz/nespresso-boutique-new-york-6?start={SpiderUS.number}"
        if self.page < 2: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            yield response.follow(next_url, callback=self.parse_reviews)
        else:
            SpiderUS.number = 0
            yield self.profile_item


    def parse_reviews(self, response):
        ratings = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[3]/section[2]/div[2]/div"""
        ).css("div[aria-label*='rating']")

        dates = response.css(".arrange-unit-fill__373c0__17z0h > .text-color--mid__373c0__3G312::text").getall()

        reviews = response.css(".comment__373c0__3EKjH .lemon--span__373c0__3997G")

        review_items = list()

        for rating, date, review in zip(ratings, dates, reviews):
            review_item = ReviewItem()

            rating = rating.xpath('@aria-label').get().split(' ')[0]
            review_item['rating'] = int(rating)

            date = self.change_date_format(date)
            review_item['date'] = date

            review_text_fragments = review.xpath('text()').getall()
            review_text = "".join(review_text_fragments)
            review_item['review'] = review_text


            review_items.append(dict(review_item))

        if not self.profile_item.get('reviews', None):
            self.profile_item['reviews'] = review_items
        else:
            self.profile_item['reviews'] += review_items

        next_url = f"https://www.yelp.com/biz/nespresso-boutique-new-york-6?start={SpiderUS.number}"
        if self.page < 2: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            yield response.follow(next_url, callback=self.parse_reviews)
        else:
            SpiderUS.number = 0
            yield self.profile_item





