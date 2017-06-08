# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging, os.path, unittest

from twisted.internet import reactor
from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime, Log


class ScraperRunTest(ScraperTest):
        

    def test_scraper(self):
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(Event.objects.get(title='Event 1').description, 'Event 1 description')

    
    def test_missing_url_elem(self):
        self.se_url.delete()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)
        
    
    def test_double(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title='Event 1', event_website=self.event_website, 
            url='http://localhost:8010/static/site_generic/event1.html',
            checker_runtime=checker_rt)
        event.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(len(Event.objects.filter(title='Event 1')), 1)
    

    def test_detail_page_url_id_field(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title='Event 1', event_website=self.event_website, 
            url='http://localhost:8010/static/site_generic/event5.html',
            checker_runtime=checker_rt)
        event.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 5)
        self.assertEqual(Event.objects.filter(title='Event 1').count(), 2)


    def test_single_standard_id_field(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title='Event 1', event_website=self.event_website, 
            url='http://localhost:8010/static/site_generic/event5.html',
            checker_runtime=checker_rt)
        event.save()
        self.soa_url.id_field = False
        self.soa_url.save()
        self.soa_title.id_field = True
        self.soa_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(Event.objects.filter(title='Event 1').count(), 1)


    def test_double_standard_id_field(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description',
            url='http://localhost:8010/static/site_generic/event5.html',
            checker_runtime=checker_rt)
        event.save()
        event = Event(title='Event 2', event_website=self.event_website,
            description='Event 1 description',
            url='http://localhost:8010/static/site_generic/event6.html',
            checker_runtime=checker_rt)
        event.save()
        event = Event(title='Event 1', event_website=self.event_website,
            description='Event 2 description',
            url='http://localhost:8010/static/site_generic/event7.html',
            checker_runtime=checker_rt)
        event.save()
        self.soa_url.id_field = False
        self.soa_url.save()
        self.soa_title.id_field = True
        self.soa_title.save()
        self.soa_desc.id_field = True
        self.soa_desc.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 6)
        self.assertEqual(Event.objects.filter(description='Event 1 description').count(), 2)

    
    def test_standard_update_field(self):
        self.soa_title.attr_type = 'T'
        self.soa_title.save()
        
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)
    
    
    def test_standard_update_field_update(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title='Event 1 - Old Title', event_website=self.event_website, 
            url='http://localhost:8010/static/site_generic/event1.html',
            checker_runtime=checker_rt)
        event.save()
        self.soa_title.attr_type = 'T'
        self.soa_title.save()
        
        self.run_event_spider(1)
        
        event_updated = Event.objects.get(pk=event.id)
        self.assertEqual(event_updated.title, 'Event 1')
        self.assertEqual(len(Event.objects.filter(title='Event 1 - Old Title')), 0)
    

    def test_save_to_db(self):
        self.soa_desc.save_to_db = False
        self.soa_desc.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(Event.objects.filter(description='Event 1 description').count(), 0)


    def test_save_to_db_non_model_attribute(self):
        self.soa_desc.name='non_model_attribute'
        self.soa_desc.save_to_db = False
        self.soa_desc.mandatory = True
        self.soa_desc.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)

    
    def test_testmode(self):
        kwargs = {
            'id': 1,
        }
        spider = EventSpider(**kwargs)
        self.process.crawl(spider, **kwargs)
        self.process.start()
        
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    @unittest.skip("Skipped, working in example project, unresolved test failure")
    def test_task_run_type(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'not_existing_site/event_main.html')
        self.event_website.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'TASK',
        }
        spider = EventSpider(**kwargs)
        self.process.crawl(spider, **kwargs)
        self.process.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 1)
        
        spider.log("Test message", logging.ERROR)
        self.assertGreater(Log.objects.count(), 0)
    
    
    def test_no_task_run_type(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'not_existing_site/event_main.html')
        self.event_website.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'SHELL',
        }
        spider = EventSpider(**kwargs)
        self.process.crawl(spider, **kwargs)
        self.process.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 0)
        
        spider.log("Test message", logging.ERROR)
        self.assertEqual(Log.objects.count(), 0)
    
    
    def test_xml_content_type(self):
        self.se_base.x_path = '//item'
        self.se_base.save()
        self.se_title.x_path = 'title/text()'
        self.se_title.save()
        self.se_url.x_path = 'link/text()'
        self.se_url.save()
        self.se_desc.x_path = 'description/text()'
        self.se_desc.from_detail_page = False
        self.se_desc.save()
        
        self.scraper.content_type = 'X'
        self.scraper.save()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_xml_content_type/event_main.xml')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 3)
    

    def test_runtime_config_max_items_read(self):        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'SHELL',
            'max_items_read': '3',
        }
        spider = EventSpider(**kwargs)
        self.process.crawl(spider, **kwargs)
        self.process.start()

        self.assertEqual(len(Event.objects.all()), 3)


    def test_runtime_config_max_items_save(self):        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'SHELL',
            'max_items_save': '3',
        }
        spider = EventSpider(**kwargs)
        self.process.crawl(spider, **kwargs)
        self.process.start()

        self.assertEqual(len(Event.objects.all()), 3)


    def test_max_items_read(self):
        self.scraper.max_items_read = 3
        self.scraper.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 3)


    def test_max_items_save(self):
        self.scraper.max_items_read = 3
        self.scraper.max_items_save = 2
        self.scraper.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
    
    
    def test_missing_mandatory(self):
        self.se_desc.mandatory = True
        self.se_desc.save()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_missing_mandatory/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)


    def test_unicode_standard_field_main_page(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_unicode/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.filter(title='Event 1 ❤ ☀ ★ ☂ ☻ ♞ ☯ ☭ ☢')), 1)
        self.assertEqual(len(Event.objects.filter(title='Event 2 雨雪天开车尤其危险')), 1)
    
    
    def test_unicode_standard_field_detail_page(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_unicode/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.filter(description='Event 1 description ♖ ☦ ✝ ❖ ➎ ♠ ♣ ♥')), 1)
        self.assertEqual(len(Event.objects.filter(description='Event 2 description Камеры наблюдения заглянули')), 1)
    

    def test_scraper_pause_status(self):
        self.scraper.status = 'P'
        self.scraper.save()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)


    def test_scraper_inactive_status(self):
        self.scraper.status = 'I'
        self.scraper.save()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)

