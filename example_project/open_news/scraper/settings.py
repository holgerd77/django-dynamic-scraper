from __future__ import unicode_literals
# Scrapy settings for open_news project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

import os, sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../../..")) #only for example_project


BOT_NAME = 'open_news'


#Setting LOG_STDOUT to True will prevent Celery scheduling to work, 2017-06-06
#If you know the cause or a fix please report on GitHub
LOG_STDOUT = False
LOG_LEVEL = 'INFO'


SPIDER_MODULES = ['dynamic_scraper.spiders', 'open_news.scraper',]
USER_AGENT = '{b}/{v}'.format(b=BOT_NAME, v='1.0')

ITEM_PIPELINES = {
    'dynamic_scraper.pipelines.DjangoImagesPipeline': 200,
    'dynamic_scraper.pipelines.ValidationPipeline': 400,
    'open_news.scraper.pipelines.DjangoWriterPipeline': 800,
}

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../thumbnails')

IMAGES_THUMBS = {
    'medium': (50, 50),
    'small': (25, 25),
}

DSCRAPER_IMAGES_STORE_FORMAT = 'ALL'

DSCRAPER_LOG_ENABLED = True
DSCRAPER_LOG_LEVEL = 'ERROR'
DSCRAPER_LOG_LIMIT = 5