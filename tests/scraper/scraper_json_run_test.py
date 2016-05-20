from __future__ import unicode_literals
import os.path, sys

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import Checker, RequestPageType, ScraperElem, SchedulerRuntime


class ScraperJSONRunTest(ScraperTest):

    def setUpScraperJSONDefaultScraper(self):
        self.se_base.x_path = 'response.events'
        self.se_base.save()
        self.se_title.x_path = 'title'
        self.se_title.save()
        self.se_url.x_path = 'url'
        self.se_url.save()
        self.se_desc.x_path = 'description'
        self.se_desc.request_page_type = 'MP'
        self.se_desc.save()
        self.se_es_1.x_path = 'title'
        self.se_es_1.save()

        self.rpt_mp.content_type = 'J'
        self.rpt_mp.save()

        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_json_content_type/event_main.json')
        self.event_website.save()

    def extraSetUpHTMLChecker(self):
        self.checker = Checker()
        self.checker.scraped_obj_attr = self.soa_url
        self.checker.scraper = self.scraper
        self.checker.checker_type = 'X'
        self.checker.checker_x_path = '//div[@class="event_not_found"]/div/text()'
        self.checker.checker_x_path_result = 'Event not found!'
        self.checker.checker_ref_url = 'http://localhost:8010/static/site_with_json_content_type/event_not_found.html'
        self.checker.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_with_json_content_type/event_not_found.html',
            checker_runtime=scheduler_rt)
        self.event.save()

    def extraSetUpJSONChecker(self):
        self.rpt_dp1.content_type = 'J'
        self.rpt_dp1.save()
        
        self.checker = Checker()
        self.checker.scraped_obj_attr = self.soa_url
        self.checker.scraper = self.scraper
        self.checker.checker_type = 'X'
        self.checker.checker_x_path = 'event_not_found'
        self.checker.checker_x_path_result = 'Event not found!'
        self.checker.checker_ref_url = 'http://localhost:8010/static/site_with_json_content_type/event_not_found.json'
        self.checker.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_with_json_content_type/event_not_found.json',
            checker_runtime=scheduler_rt)
        self.event.save()


    def test_num_scraped_objects(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        #logging.info(unicode(Event.objects.all()))
        self.assertEqual(len(Event.objects.all()), 3)


    def test_non_repetition(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(title='Event 1')), 1)


    def test_non_data_mixing(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(Event.objects.get(pk=1).title, 'Event 1')
        self.assertEqual(Event.objects.get(pk=1).description, 'Event 1 Description')
    
    
    def test_static_processor_empty_x_path(self):
        self.setUpScraperJSONDefaultScraper()
        self.se_title.x_path = ''
        self.se_title.processors = 'static'
        self.se_title.proc_ctxt = "'static': 'This text should always be there'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.filter(title='This text should always be there')), 3)
    

    def test_detail_page(self):
        self.setUpScraperJSONDefaultScraper()
        self.se_desc.x_path = '//div/div[@class="description"]/text()'
        self.se_desc.request_page_type = 'DP1'
        self.se_desc.save()
        self.run_event_spider(1)
        #logging.info(unicode(Event.objects.all()))
        self.assertEqual(len(Event.objects.filter(description='Event Detail Page 1 Description')), 1)


    def test_detail_page_json(self):
        self.setUpScraperJSONDefaultScraper()
        self.rpt_dp1.content_type = 'J'
        self.rpt_dp1.save()
        self.se_url.x_path = 'json_url'
        self.se_url.save()
        self.se_desc.x_path = 'event_details.description'
        self.se_desc.request_page_type = 'DP1'
        self.se_desc.save()
        self.run_event_spider(1)
        #logging.info(unicode(Event.objects.all()))
        self.assertEqual(len(Event.objects.filter(description='Event Detail Page 1 Description')), 1)


    def test_multiple_detail_pages(self):
        self.setUpScraperJSONDefaultScraper()
        self.se_desc.x_path = '//div/div[@class="description2"]/text()'
        self.se_desc.request_page_type = 'DP1'
        self.se_desc.save()

        self.soa_url.id_field = False
        self.soa_url.save_to_db = False
        self.soa_url.save()

        self.soa_url2.save_to_db = False
        self.soa_url2.save()

        self.rpt_dp2 = RequestPageType(page_type='DP2', scraper=self.scraper, scraped_obj_attr=self.soa_url2, content_type='J')
        self.rpt_dp2.save()
        
        self.se_url2 = ScraperElem(scraped_obj_attr=self.soa_url2, scraper=self.scraper, 
            x_path='json_url', request_page_type='MP')
        self.se_url2.save()
        
        self.se_desc2 = ScraperElem(scraped_obj_attr=self.soa_desc2, scraper=self.scraper, 
            x_path='event_details.description2', request_page_type='DP2', mandatory=False)
        self.se_desc2.save()
        

        self.run_event_spider(1)
        #logging.info(unicode(Event.objects.all()))
        events = Event.objects.filter(
            title='Event 1',
            #url='http://localhost:8010/static/site_with_json_content_type/event1.html',
            #url2='http://localhost:8010/static/site_with_json_content_type/event1.json',
            #description='Event Detail Page 1 Description HTML',
            description2='Event Detail Page 1 Description JSON',
        )
        self.assertEqual(len(events), 1)
    
    
    def test_json_array(self):
        self.setUpScraperJSONDefaultScraper()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_json_content_type/event_main_array.json')
        self.event_website.save()
        
        self.se_base.x_path = '$'
        self.se_base.save()
        
        self.run_event_spider(1)
        #logging.info(unicode(Event.objects.all()))
        self.assertEqual(len(Event.objects.all()), 3)


    def test_checker_x_path_type_x_path_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpHTMLChecker()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)


    def test_checker_x_path_type_x_path_no_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpHTMLChecker()
        self.checker.checker_x_path = '//div[@class="this_is_the_wrong_xpath"]/div/text()'
        self.checker.save()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)


    def test_json_checker_x_path_type_x_path_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpJSONChecker()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)


    def test_json_checker_x_path_type_x_path_no_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpJSONChecker()
        self.checker.checker_x_path = 'this_is_the_wrong_xpath'
        self.checker.save()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)





