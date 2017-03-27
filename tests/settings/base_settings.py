from __future__ import unicode_literals
# Scrapy settings for unit tests
import os, sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../.."))

ITEM_PIPELINES = {
    'dynamic_scraper.pipelines.DjangoImagesPipeline': 200,
    'dynamic_scraper.pipelines.ValidationPipeline': 400,
    'scraper.scraper_test.DjangoWriterPipeline': 800,
}

#ScrapyJS/Splash
SPLASH_URL = 'http://127.0.0.1:8050/'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

DSCRAPER_SPLASH_ARGS = {
    'wait': 0.3
}
#END

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../scraper/imgs')

DSCRAPER_IMAGES_STORE_FORMAT = 'FLAT'

