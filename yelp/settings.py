BOT_NAME = 'yelp'

SPIDER_MODULES = ['yelp.spiders']
NEWSPIDER_MODULE = 'yelp.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}

DOWNLOADER_MIDDLEWARES = {
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}

ITEM_PIPELINES = {
   'yelp.pipelines.YelpPipeline': 300,
   'yelp.pipelines.DuplicationDetectorPipeline': 400,
   'yelp.pipelines.WriterPipeline': 800,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 7
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5

HTTPCACHE_ENABLED = True

DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# ROTATING_PROXY_LIST = [
#     'proxy1.com:8000',
#     'proxy2.com:8031',
# ]