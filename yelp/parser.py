import pendulum

from yelp.items import ProfileItem, ReviewItem


class ProfileParser:

    def parse_profile_data(self, response):
        profile_item = ProfileItem()
        profile_item['name'] = self.__parse_name(response)
        profile_item['category'] = self.__parse_category(response)
        profile_item['phone'] = self.__parse_phone(response)
        address, city = self.__parse_address(response)
        profile_item['city'] = city
        profile_item['address'] = address
        profile_item['reviews'] = []

        return profile_item

    def __parse_name(self, response):
        name = response.css("h1::text").get()
        return name

    def __parse_category(self, response):
        categories = response.css(".text-size--large__373c0__1568g .link-size--inherit__373c0__2JXk5::text").getall()
        category = " > ".join(categories)
        return category

    def __parse_phone(self, response):
        phone = response.css(".icon--24-phone").xpath("../../div[2]/p[2]/text()").get()
        return phone

    def __parse_address(self, response):
        address_parts = response.css("address > span").css("::text").getall()
        if address_parts:
            address = ", ".join(address_parts)
            if address_parts[-1].isnumeric():
                city = address_parts[-2]
            else:
                city = address_parts[-1]
        else:
            address = None
            city = None

        try:
            city_name = city.split(', ')[0]
        except AttributeError:
            city_name = None

        return address, city_name


class ReviewParser:

    def change_date_format(self, date):
        try:
            dt = pendulum.from_format(date, 'M/D/YYYY')
        except TypeError:
            return None
        else:
            return dt.to_date_string()

    def __parse_rating(self, review):
        rating_text = review.css("div[aria-label*='rating']").xpath("@aria-label").get()
        try:
            rating = rating_text.split(' ')[0]
            rating = int(rating)
        except (ValueError, AttributeError):
            rating = None
        finally:
            return rating

    def __parse_date(self, review):
        date = review.xpath(""".//span[contains(text(),'/20')]/text()""").get()
        date = self.change_date_format(date)
        return date

    def __parse_review_text(self, review):
        span = review.xpath(".//span[@lang]").css("::text").getall()
        review_text = "".join(span).replace("\xa0", "")
        return review_text

    def parse_reviews(self, response):
        all_reviews = response.css(".layout-stack-small__373c0__3cHex")

        review_items = list()
        for review in all_reviews:
            review_item = ReviewItem()

            review_item['rating'] = self.__parse_rating(review)

            review_item['date'] = self.__parse_date(review)

            review_item['review'] = self.__parse_review_text(review)

            if review_item['rating'] and review_item['date'] and review_item['review']:
                review_items.append(dict(review_item))

        return review_items
