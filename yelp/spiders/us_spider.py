import scrapy
import pendulum

from yelp.items import ProfileItem, ReviewItem


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    number = 20
    start_urls = [
        "https://www.yelp.com/biz/nespresso-boutique-new-york-6?start=0"
    ]

    def change_date_format(date):
        dt = pendulum.from_format(date, 'M/D/YYYY')
        return dt.to_date_string()

    def parse(self, response):
        # TODO do not collect toese data every single time
        # TODO encoding
        profile_item = ProfileItem()
        name = response.css("h1::text").get()

        categories = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/span[2]/span/a/text()"""
        ).getall()
        category = " > ".join(categories)

        phone = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[2]/div/div/section[2]/div/div[2]/div/div[2]/p[2]/text()"""
        ).get()

        street = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/address/p[1]/span/text()"""
        ).get()

        city = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/address/p[2]/span/text()"""
        ).get()

        addr = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/div/p[1]/text()"""
        ).get()

        addr2 = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/div/p[2]/text()"""
        ).get()

        address = f"{street}, {city}, {addr}, {addr2}"

        city_name = city.split(', ')[0]

        profile_item['name'] = name
        profile_item['category'] = category
        profile_item['phone'] = phone
        profile_item['city'] = city_name
        profile_item['address'] = address

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

            date = SpiderUS.change_date_format(date)
            review_item['date'] = date

            review_text_fragments = review.xpath('text()').getall()
            review_text = "".join(review_text_fragments)
            review_item['review'] = review_text


            review_items.append(dict(review_item))

        profile_item['reviews'] = review_items

        yield profile_item

        next_url = f"https://www.yelp.com/biz/nespresso-boutique-new-york-6?start={SpiderUS.number}"
        if SpiderUS.number < 40:
            SpiderUS.number += 20
            yield response.follow(next_url, callback=self.parse)





