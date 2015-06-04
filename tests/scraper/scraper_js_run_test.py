import os

from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest


class ScraperJSRunTest(ScraperTest):
    
    def setUpScraperJSDefaultScraper(self):
        self.event_website.url = os.path.join('http://localhost:8010/static/', 'site_with_js/event_main.html')
        self.event_website.save()

    def setUpScraperJSDockerScraper(self):
        self.event_website.url = os.path.join('http://10.0.2.2:8010/static/', 'site_with_js/event_main_docker.html')
        self.event_website.save()


    def test_default_no_scrapyjs_main_page(self):
        self.setUpScraperJSDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 1)

    def test_default_no_scrapyjs_detail_page(self):
        self.setUpScraperJSDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(description='Event 1 description')), 1)

    def test_activated_scrapyjs_main_page(self):
        self.setUpScraperJSDockerScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 2)

    def test_activated_scrapyjs_detail_page(self):
        self.setUpScraperJSDockerScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(description='Event 1 JS description')), 1)