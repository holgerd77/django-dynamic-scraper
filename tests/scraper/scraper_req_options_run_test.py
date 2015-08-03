import os, unittest
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest


class ScraperReqOptionsRunTest(ScraperTest):

    def setUpWithCookiesScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/cookies/', '%s.html' % test_case)
        self.event_website.save()

        self.scraper.cookies = '{ "simple": "SIMPLE_VALUE" }'
        self.scraper.save()

    @unittest.skip("Skipped, cookies are not sent in test case environment, no solution yet!")
    def test_with_cookies_simple(self):
        self.setUpWithCookiesScraper('simple')
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)