import os

from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest


class ScraperJSRunTest(ScraperTest):
    
    def setUpScraperJSScraper(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_js/event_main.html')
        self.event_website.save()

    def test_default_no_scrapyjs(self):
        self.setUpScraperJSScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 1)