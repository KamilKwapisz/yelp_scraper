import scrapy


class ProfileItem(scrapy.Item):
    name = scrapy.Field()
    phone = scrapy.Field()
    category = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    reviews = scrapy.Field()


class ReviewItem(scrapy.Item):
    rating = scrapy.Field()
    review = scrapy.Field()
    date = scrapy.Field()  # YYYY-MM-DD
