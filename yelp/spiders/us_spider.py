import scrapy
from scrapy.exceptions import CloseSpider
import pendulum
from user_agent import generate_user_agent

from yelp.items import ProfileItem, ReviewItem

# TODO: concatenating start parameter

class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    number = 20
    page = 1
    max_page_number = None

    search_page = 1
    profile_search_max_page = None
    start_urls = [
        # "https://www.yelp.com/biz/nespresso-boutique-new-york-6?start=0",
        # "https://www.yelp.com/search?cflt=hotels&find_loc=San%20Francisco%2C%20CA&start=0"
    ]
    profile_item = None
    profile_links = list()

    parsing_profile_page = True


    def __init__(self, profile_url=None, list_url=None, *args, **kwargs):
        super(SpiderUS, self).__init__(*args, **kwargs)
        if profile_url:
            self.parsing_profile_page = True
            self.start_urls = [profile_url]
        elif list_url:
            self.parsing_profile_page = False
            self.start_urls = [list_url]
        else:
            # raise CloseSpider('ivalid_argument')
            pass

            
    def change_date_format(self, date):
        dt = pendulum.from_format(date, 'M/D/YYYY')
        return dt.to_date_string()

    def start_requests(self):
        if self.parsing_profile_page:
            yield scrapy.Request(
                url=self.start_urls[0], 
                callback=self.parse_profile
                # headers={'User-Agent': }
            )
        else:
            yield scrapy.Request(self.start_urls[0], self.parse_profile_list)
    
    # def parse_profile_list(self, response):
    #     pagination = response.css(".text-align--center__373c0__2n2yQ .text-align--left__373c0__2XGa-::text").get()
    #     self.profile_search_max_page = int(pagination.split(' ')[-1])

    #     self.profile_links += response.css("h4 > span > a").css("::attr(href)").getall()

    #     # TODO getting further pagination
    #     # if self.search_page < self.profile_search_max_page:
    #     if self.search_page < 3:
    #         next_page_url = response.xpath("""//*[@id="wrap"]/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div/div[1]/div/div[11]/span/a/@href""").get()
    #         if next_page_url:
    #             self.search_page += 1
    #             print("follow ->", next_page_url)
    #             yield response.follow(next_page_url, callback=self.parse_profile_list)
    #     else:
    #         print(self.profile_links)
    #         try:
    #             profile_link = self.profile_links.pop(0)
    #             yield response.follow(profile_link, callback=self.parse_profile)
    #         except IndexError:
    #             print("#################DONE")


    def parse_profile(self, response):
        self.profile_item = ProfileItem()
        name = response.css("h1::text").get()

        categories = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/div/div/span[2]/span/a/text()"""
        ).getall()
        category = " > ".join(categories)

        phone = response.xpath(
            """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[2]/div/div/section[2]/div/div[2]/div/div[2]/p[2]/text()"""
        ).get(None)

        # street = response.xpath(
        #     """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[3]/div[2]/div[1]/div/div/div/div[1]/address/p[1]/span/text()"""
        # ).get()

        # city = response.xpath(
        #     """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[2]/div[2]/div[1]/div/div/div/div[1]/address/p[2]/span/text()"""
        # ).get(None)

        # addr = response.xpath(
        #     """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[2]/div[2]/div[1]/div/div/div/div[1]/div/p[1]/text()"""
        # ).get(None)

        # addr2 = response.xpath(
        #     """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/section[2]/div[2]/div[1]/div/div/div/div[1]/div/p[2]/text()"""
        # ).get(None)

        address_parts = response.css("address > span").css("::text").getall()
        if address_parts:
            address = "".join(address_parts)
            if address_parts[-1].isnumeric():
                city = address_parts[-2]
            else:
                city = address_parts[-1]
        else:
            address = None
            city = None
        

        # address = f"{street}, {city}, {addr}, {addr2}"

        try:
            city_name = city.split(', ')[0]
        except AttributeError:
            city_name = None

        self.profile_item['name'] = name
        self.profile_item['category'] = category
        self.profile_item['phone'] = phone
        self.profile_item['city'] = city_name
        self.profile_item['address'] = address

        pagination = response.xpath(
            """//div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[3]/section[2]/div[2]/div/div[4]/div[1]/span/text()"""
        ).get(None)

        # TODO fix
        # self.max_page_number = int(pagination.split(" ")[-1])
        self.max_page_number = 3
        
        # next_url = f"https://www.yelp.com/biz/nespresso-boutique-new-york-6?start={SpiderUS.number}"
        next_url = response.url
        if "start=" in next_url:
            start_index = next_url.index("t=") + 2
            next_url = next_url[:start_index] + f"{SpiderUS.number}"
        else:
            next_url += f"?start={SpiderUS.number}"

        if self.page < 2: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            yield response.follow(next_url, callback=self.parse_reviews)
        else:
            SpiderUS.number = 0
            yield self.profile_item

            # try:
            #     profile_link = self.profile_links.pop(0)
            #     yield response.follow(profile_link, callback=self.parse_profile)
            # except IndexError:
            #     print("#################DONE")


    def parse_reviews(self, response):
        all_reviews = response.css(".layout-stack-small__373c0__3cHex")
        
        # ratings = response.xpath(
        #     """//*[@id="wrap"]/div[3]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[3]/section[2]/div[2]/div"""
        # ).css("div[aria-label*='rating']")

        ratings = all_reviews.css("div[aria-label*='rating']").xpath("@aria-label").getall()

        # dates = response.css(".arrange-unit-fill__373c0__17z0h > .text-color--mid__373c0__3G312::text").getall()
        dates = all_reviews.xpath(""".//span[contains(text(),'/20')]/text()""").getall()

        # reviews = response.css(".comment__373c0__3EKjH .lemon--span__373c0__3997G")
        reviews_spans= all_reviews.xpath(".//span[@lang]")

        reviews_content = list()
        for span in reviews_spans:
            texts = span.css("::text").getall()
            reviews_content.append("".join(texts).replace("\xa0", ""))

        if len(ratings) == len(dates) == len(reviews_content):
            review_items = list()

            for rating, date, review in zip(ratings, dates, reviews_content):
                review_item = ReviewItem()

                rating = rating.split(' ')[0]
                review_item['rating'] = int(rating)

                date = self.change_date_format(date)
                review_item['date'] = date

                review_item['review'] = review

                review_items.append(dict(review_item))
            

            if not self.profile_item.get('reviews', None):
                self.profile_item['reviews'] = review_items
            else:
                self.profile_item['reviews'] += review_items

        next_url = response.url
        if "start=" in next_url:
            start_index = next_url.index("t=") + 2
            next_url = next_url[:start_index] + f"{SpiderUS.number}"
        else:
            next_url += f"?start={SpiderUS.number}"

        if self.page < 3: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            yield response.follow(next_url, callback=self.parse_reviews)
        else:
            SpiderUS.number = 0
            yield self.profile_item

            # try:
            #     profile_link = self.profile_links.pop(0)
            #     yield response.follow(profile_link, callback=self.parse_profile)
            # except IndexError:
            #     print("#################DONE")





