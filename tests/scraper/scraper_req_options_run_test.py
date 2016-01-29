from __future__ import unicode_literals
import os, unittest
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest


class ScraperReqOptionsRunTest(ScraperTest):

    def setUpWithRequestTypeMethodScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/request_type_method/', '{tc}.html'.format(tc=test_case))
        self.event_website.save()


    def setUpWithHeaderBodyDataScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/header_body_data/', '{tc}.html'.format(tc=test_case))
        self.event_website.save()


    def setUpWithFormDataScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/form_data/', '{tc}.html'.format(tc=test_case))
        self.event_website.save()

        self.rpt_mp.request_type = 'F'
        self.rpt_mp.method = "POST"
        self.rpt_mp.save()


    def setUpWithFormDataPagination(self):              
        self.scraper.pagination_type = 'F'
        self.scraper.pagination_append_str = ''
        self.scraper.pagination_on_start = True
        self.scraper.pagination_page_replace = "'1', '2',"
        self.scraper.save()

        self.rpt_mp.form_data = '{ "page": "{page}" }'
        self.rpt_mp.save()


    def setUpWithCookiesScraper(self, test_case):
        self.event_website.url = os.path.join('http://localhost:8010/scraper/cookies/', '{tc}.html'.format(tc=test_case))
        self.event_website.save()

        self.rpt_mp.cookies = '{ "simple": "SIMPLE_VALUE" }'
        self.rpt_mp.save()


    def test_with_request_type_post(self):
        self.setUpWithRequestTypeMethodScraper('post')
        self.rpt_mp.method = "POST"
        self.rpt_mp.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_with_custom_header(self):
        self.setUpWithHeaderBodyDataScraper('header')
        self.rpt_mp.headers = '{ "Referer": "http://comingfromhere.io" }'
        self.rpt_mp.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_with_custom_body(self):
        self.setUpWithHeaderBodyDataScraper('body')
        self.rpt_mp.method = "POST"
        self.rpt_mp.body = 'This is the HTTP request body content.'
        self.rpt_mp.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_with_form_data_simple(self):
        self.setUpWithFormDataScraper('simple')
        self.rpt_mp.form_data = '{ "simple": "SIMPLE_VALUE" }'
        self.rpt_mp.save()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_with_form_data_pagination(self):
        self.setUpWithFormDataScraper('page')
        self.setUpWithFormDataPagination()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 7)


    @unittest.skip("Skipped, cookies are not sent in test case environment, no solution yet!")
    def test_with_cookies_simple(self):
        self.setUpWithCookiesScraper('simple')
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)
