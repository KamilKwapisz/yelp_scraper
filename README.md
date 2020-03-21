# yelp_scraper
Yelp scraper for test task

# Running
```scrapy crawl us_spider -a profile_url="https://www.yelp.com/biz/nespresso-boutique-new-york-6"```

```scrapy crawl us_spider -a list_url="https://www.yelp.com/search?cflt=hotels&find_loc=New+York%2C+NY"```

# Comment
I haven't done the Portugal version. I've seen that the reviews are loaded from JS. I've tried using Splash but faced some serious problems with docker, sorry. 

I've sticked with passing profile_url or list_url as a typical scrapy parameter. I hope it's okay :) 
