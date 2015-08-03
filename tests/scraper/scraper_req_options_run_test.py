import os, unittest
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest


class ScraperReqOptionsRunTest(ScraperTest):

    def setUpWithFormDataScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/form_data/', '%s.html' % test_case)
        self.event_website.save()

        self.scraper.request_type = 'F'
        self.scraper.form_data = '{ "simple": "SIMPLE_VALUE" }'
        self.scraper.save()


    def setUpWithFormDataPagination(self):              
        self.scraper.pagination_type = 'F'
        self.scraper.pagination_append_str = ''
        self.scraper.pagination_on_start = True
        self.scraper.pagination_page_replace = "'1', '2',"
        self.scraper.form_data = '{ "page": "{page}" }'
        self.scraper.save()

    def setUpWithCookiesScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/cookies/', '%s.html' % test_case)
        self.event_website.save()

        self.scraper.cookies = '{ "simple": "SIMPLE_VALUE" }'
        self.scraper.save()


    def test_with_form_data_simple(self):
        self.setUpWithFormDataScraper('simple')
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_with_form_data_pagination(self):
        self.setUpWithFormDataScraper('pagination')
        self.setUpWithFormDataPagination()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 7)


    @unittest.skip("Skipped, cookies are not sent in test case environment, no solution yet!")
    def test_with_cookies_simple(self):
        self.setUpWithCookiesScraper('simple')
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)