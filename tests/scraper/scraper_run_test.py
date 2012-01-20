import datetime
import os.path

from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime


class ScraperRunTest(ScraperTest):
    
    
    def test_missing_base_elem(self):
        self.se_base.delete()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)


    def test_missing_url_elem(self):
        self.se_url.delete()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)
        

    def test_scraper(self):
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(Event.objects.get(title='Event 1').description, u'Event 1 description')
    
    
    def test_double(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title=u'Event 1', url=u'http://localhost:8010/static/site_generic/event1.html',
            checker_runtime=checker_rt)
        event.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(len(Event.objects.filter(title='Event 1')), 1)
        
    
    def test_testmode(self):
        kwargs = {
            'id': 1,
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_task_run_type(self):
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'not_existing_site/event_main.html')
        self.scraper_rt.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'TASK',
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 1)
    
    
    def test_no_task_run_type(self):
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'not_existing_site/event_main.html')
        self.scraper_rt.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'SHELL',
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 0)
        
        
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
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'site_missing_mandatory/event_main.html')
        self.scraper_rt.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
    
    
    def test_processor(self):
        self.se_url.processors = u'pre_url'
        self.se_url.proc_ctxt = u"'pre_url': 'http://localhost:8010/static/site_with_processor/'"
        self.se_url.save()
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'site_with_processor/event_main.html')
        self.scraper_rt.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
    
    
    def test_reg_exp(self):
        self.se_desc.reg_exp = u'(\d{6})'
        self.se_desc.save()
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'site_with_reg_exp/event_main.html')
        self.scraper_rt.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(Event.objects.get(title='Event 1').description, '563423')
    
    
    def test_with_imgs(self):
        path1 = os.path.join(self.PROJECT_ROOT, 'imgs/1d7c0c2ea752d7aa951e88f2bc90a3f17058c473.jpg')
        if os.access(path1, os.F_OK):
            os.unlink(path1)
        path2 = os.path.join(self.PROJECT_ROOT, 'imgs/3cfa4d48e423c5eb3d4f6e9b5e5d373036ac5192.jpg')
        if os.access(path2, os.F_OK):
            os.unlink(path2)
        self.se_desc.mandatory = True
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.scraper_rt.url = os.path.join(self.SERVER_URL, 'site_with_imgs/event_main.html')
        self.scraper_rt.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(Event.objects.get(title='Event 1').description, '1d7c0c2ea752d7aa951e88f2bc90a3f17058c473.jpg')
        self.assertTrue(os.access(path1, os.F_OK))
        self.assertTrue(os.access(path2, os.F_OK))
        