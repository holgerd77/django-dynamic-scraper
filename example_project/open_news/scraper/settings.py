# Scrapy settings for open_news project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

import sys
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path = sys.path + [os.path.join(PROJECT_ROOT, '../../..'), os.path.join(PROJECT_ROOT, '../..')]

from django.core.management import setup_environ
import example_project.settings
setup_environ(example_project.settings)


BOT_NAME = 'open_news'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['dynamic_scraper.spiders', 'open_news.scraper',]
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = [
    'dynamic_scraper.pipelines.DjangoImagesPipeline',
    'dynamic_scraper.pipelines.ValidationPipeline',
    'open_news.scraper.pipelines.DjangoWriterPipeline',
]

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../thumbnails')

IMAGES_THUMBS = {
    'small': (170, 170),
}

DSCRAPER_LOG_ENABLED = True
DSCRAPER_LOG_LEVEL = 'INFO'
DSCRAPER_LOG_LIMIT = 5