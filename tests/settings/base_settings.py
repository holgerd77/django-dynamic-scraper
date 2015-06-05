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
SPLASH_URL = 'http://192.168.59.103:8050'
DUPEFILTER_CLASS = 'scrapyjs.SplashAwareDupeFilter'

DOWNLOADER_MIDDLEWARES = {
    'scrapyjs.SplashMiddleware': 725,
}

DSCRAPER_SPLASH_ARGS = {
    'wait': 0.3
}
#END

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../scraper/imgs')

DSCRAPER_IMAGES_STORE_FORMAT = 'FLAT'

