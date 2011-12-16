import os.path
from scraper.models import Event
from scraper.scraper_test import ScraperTest
from scrapy.exceptions import CloseSpider


class PaginationTest(ScraperTest):


    def setUp(self):
        super(PaginationTest, self).setUp()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_generic/event_main')
        self.event_website.save()
        
        self.scraper.use_pagination = True
        self.scraper.pagination_append_str = '{page}.html'
        self.scraper.pagination_on_start = True
        self.scraper.pagination_range = '1,3'
        self.scraper.save()


    def test_config_append_str_without_page(self):
        self.scraper.pagination_append_str = '.html'
        self.scraper.save()
        
        self.assertRaises(CloseSpider, self.run_event_spider, 1)

    
    def test_config_wrong_range_format(self):
        self.scraper.pagination_range = '1,3,4,7'
        self.scraper.save()
        
        self.assertRaises(CloseSpider, self.run_event_spider, 1)
        

    def test_p_on_start(self):        
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 7)


    def test_one_page(self):
        self.scraper.pagination_range = '1,2'
        self.scraper.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)