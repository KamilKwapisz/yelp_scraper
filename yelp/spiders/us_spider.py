import scrapy
from scrapy.exceptions import CloseSpider
from user_agent import generate_user_agent

from yelp.items import ProfileItem, ReviewItem
from yelp.parser import ProfileParser, ReviewParser


class SpiderUS(scrapy.Spider):
    name = 'us_spider'
    allowed_domains = ['yelp.com']
    number = 20
    page = 1
    max_page_number = None

    search_page = 1
    profile_search_max_page = None
    start_urls = []
    profile_item = None
    profile_links = list()

    parsing_profile_page = True

    profile_parser = ProfileParser()
    review_parser = ReviewParser()

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

    def start_requests(self):
        if self.parsing_profile_page:
            yield scrapy.Request(url=self.start_urls[0], callback=self.parse_profile)
        else:
            yield scrapy.Request(self.start_urls[0], self.parse_profile_list)
    
    def get_next_url(self, url):
        if "start=" in url:
            start_index = url.index("t=") + 2
            next_url = url[:start_index] + f"{SpiderUS.number}"
        else:
            next_url = url + f"?start={SpiderUS.number}"
        return next_url
    
    def parse_profile_list(self, response):
        pagination = response.xpath("//span[contains(text(), ' of ')]/text()").get()
        self.profile_search_max_page = 2

        links = response.css("h4 > span > a").css("::attr(href)").getall()
        links = [link for link in links if link.startswith('/biz')]  # getting rid of sponsored
        self.profile_links += links
        self.profile_links = list(set(self.profile_links))

        # if self.search_page < self.profile_search_max_page:
        if self.search_page < 3:
            paginator_div = response.css("div.pagination-links-container__373c0__1vHLX")
            next_page_url = paginator_div.xpath(".//div/div[last()]/span/a/@href").get()
            if next_page_url:
                self.search_page += 1
                yield response.follow(next_page_url, callback=self.parse_profile_list)
        else:
            print(self.profile_links)
            try:
                profile_link = self.profile_links.pop(0)
                yield response.follow(profile_link, callback=self.parse_profile)
            except IndexError:
                print("#################DONE")


    def parse_profile(self, response):
        print("PROFILEEEEEEEEEEEEEEE", response.url)

        self.profile_item = self.profile_parser.parse_profile_data(response)

        reviews = self.review_parser.parse_reviews(response)

        self.profile_item['reviews'] += reviews
        print("REVS AFTER 1 REQ IS ", len(self.profile_item['reviews']))

        pagination = response.xpath("//span[contains(text(), 'Page ')]/text()").get()
        # self.max_page_number = int(pagination.split(" ")[-1])
        self.max_page_number = 3
        
        next_url = self.get_next_url(response.url)
        print(next_url, self.page)

        if self.page < 3: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            print("FOLLOWING review")
            yield response.follow(next_url, callback=self.parse_reviews, priority=2)
        else:
            self.page = 1
            SpiderUS.number = 0
            print("here yielding", response.url)
            yield self.profile_item

            if self.profile_links:
                SpiderUS.number = 0
                self.page = 1
                profile_link = self.profile_links.pop(0)
                yield response.follow(profile_link, callback=self.parse_profile, priority=1)

    def parse_reviews(self, response):
        print("PARSING  ", response.url)

        reviews = self.review_parser.parse_reviews(response)
        self.profile_item['reviews'] += reviews

        next_url = self.get_next_url(response.url)
        print(next_url, self.page)

        if self.page < 3: #self.max_page_number:
            SpiderUS.number += 20
            self.page += 1
            yield response.follow(next_url, callback=self.parse_reviews)
        else:
            SpiderUS.number = 0
            self.page = 1
            print("here222 yielding", len(self.profile_item['reviews']))
            yield self.profile_item

            if self.profile_links:
                self.page = 1
                SpiderUS.number = 0
                profile_link = self.profile_links.pop(0)
                yield response.follow(profile_link, callback=self.parse_profile, priority=2)
