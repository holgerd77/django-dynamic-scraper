from __future__ import unicode_literals
import os.path, unittest
from scraper.models import Event
from scraper.scraper_test import ScraperTest
from scrapy.exceptions import CloseSpider


class PaginationTest(ScraperTest):


    def setUpPaginationRangeFunctTypeScraper(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_generic/event_main')
        self.event_website.save()
              
        self.scraper.pagination_type = 'R'
        self.scraper.pagination_append_str = '{page}.html'
        self.scraper.pagination_on_start = True
        self.scraper.pagination_page_replace = '1,3'
        self.scraper.save()


    def setUpPaginationFreeListTypeScraper(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_generic/')
        self.event_website.save()
              
        self.scraper.pagination_type = 'F'
        self.scraper.pagination_append_str = '{page}.html'
        self.scraper.pagination_on_start = True
        self.scraper.pagination_page_replace = "'event_main1', 'event_main2',"
        self.scraper.save()


    def test_config_empty_append_str(self):
        self.setUpPaginationRangeFunctTypeScraper()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_generic/event_main.html')
        self.event_website.save()
        self.scraper.pagination_append_str = ''
        self.scraper.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_config_append_str_without_page(self):
        self.setUpPaginationRangeFunctTypeScraper()
        self.scraper.pagination_append_str = '.html'
        self.scraper.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)


    def test_p_on_start(self):
        self.setUpPaginationRangeFunctTypeScraper()   
        self.run_event_spider(1)

        self.assertEqual(len(Event.objects.all()), 7)

    
    @unittest.skip("Skipped, CloseSpider not visible in test anymore after having reworked settings initialization")
    def test_range_funct_type_wrong_replace_format(self):
        self.setUpPaginationRangeFunctTypeScraper() 
        self.scraper.pagination_page_replace = '1,3,4,7'
        self.scraper.save()
        
        self.assertRaises(CloseSpider, self.run_event_spider, 1)


    def test_range_funct_type_one_page(self):
        self.setUpPaginationRangeFunctTypeScraper()
        self.scraper.pagination_page_replace = '1,2'
        self.scraper.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
    
    
    @unittest.skip("Skipped, CloseSpider not visible in test anymore after having reworked settings initialization")
    def test_free_list_type_wrong_replace_format(self):
        self.setUpPaginationFreeListTypeScraper()
        
        self.scraper.pagination_page_replace = "'Oh I forgot a closing bracket what a mess, "
        self.scraper.save()
        
        self.assertRaises(CloseSpider, self.run_event_spider, 1)
        

    def test_free_list_type_scraper_run(self):
        self.setUpPaginationFreeListTypeScraper()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 7)