import os.path

from scrapy import log
from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime, Log


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
    
    
    def test_standard_field_as_detail_page_url_hack(self):
        self.se_desc.x_path = u'a/text()'
        self.se_desc.from_detail_page = False
        self.se_desc.save()
        self.soa_title.attr_type = 'U'
        self.soa_title.save()
        self.soa_url.attr_type = 'S'
        self.soa_url.save()
        
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        
    
    def test_double(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title=u'Event 1', event_website=self.event_website, 
            url=u'http://localhost:8010/static/site_generic/event1.html',
            checker_runtime=checker_rt)
        event.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 4)
        self.assertEqual(len(Event.objects.filter(title='Event 1')), 1)
    
    
    def test_standard_update_field(self):
        self.soa_title.attr_type = 'T'
        self.soa_title.save()
        
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 4)
    
    
    def test_standard_update_field_update(self):
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        event = Event(title=u'Event 1 - Old Title', event_website=self.event_website, 
            url=u'http://localhost:8010/static/site_generic/event1.html',
            checker_runtime=checker_rt)
        event.save()
        self.soa_title.attr_type = 'T'
        self.soa_title.save()
        
        self.run_event_spider(1)
        
        event_updated = Event.objects.get(pk=event.id)
        self.assertEqual(event_updated.title, 'Event 1')
        self.assertEqual(len(Event.objects.filter(title='Event 1 - Old Title')), 0)
    
    
    def test_testmode(self):
        kwargs = {
            'id': 1,
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_task_run_type(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'not_existing_site/event_main.html')
        self.event_website.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'TASK',
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 1)
        
        spider.log("Test message", log.ERROR)
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
        self.crawler.crawl(spider)
        self.crawler.start()
        
        self.assertEqual(spider.scheduler_runtime.num_zero_actions, 0)
        
        spider.log("Test message", log.ERROR)
        self.assertEqual(Log.objects.count(), 0)
    
    
    def test_xml_content_type(self):
        self.se_base.x_path = u'//item'
        self.se_base.save()
        self.se_title.x_path = u'title/text()'
        self.se_title.save()
        self.se_url.x_path = u'link/text()'
        self.se_url.save()
        self.se_desc.x_path = u'description/text()'
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
        self.crawler.crawl(spider)
        self.crawler.start()

        self.assertEqual(len(Event.objects.all()), 3)


    def test_runtime_config_max_items_save(self):        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'SHELL',
            'max_items_save': '3',
        }
        spider = EventSpider(**kwargs)
        self.crawler.crawl(spider)
        self.crawler.start()

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
    
    
    def test_scraper_pause_status(self):
        self.scraper.status = 'P'
        self.scraper.save()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)


    def test_scraper_inactive_status(self):
        self.scraper.status = 'I'
        self.scraper.save()
        self.assertRaises(CloseSpider, self.run_event_spider, 1)
    
    
    def setUpProcessorTest(self):
        self.se_url.processors = u'pre_url'
        self.se_url.proc_ctxt = u"'pre_url': 'http://localhost:8010/static/site_with_processor/'"
        self.se_url.save()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_processor/event_main.html')
        self.event_website.save()


    def test_processor(self):
        self.setUpProcessorTest()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
    
    
    def test_multiple_processors_use(self):
        self.setUpProcessorTest()
        self.se_desc.processors = u'pre_string, post_string '
        self.se_desc.proc_ctxt = u"'pre_string': 'before_', 'post_string': '_after',"
        self.se_desc.save()
        
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.get(id=1).description, 'before_Event 2 description_after')
    
    
    def test_replace_processor_wrong_x_path(self):
        self.setUpProcessorTest()
        self.se_title.x_path = u'/div[@class="class_which_is_not_there"]/text()'
        self.se_title.processors = u'replace'
        self.se_title.proc_ctxt = u"'replace': 'This text is a replacement'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 0)


    def test_replace_processor_correct_x_path(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'replace'
        self.se_title.proc_ctxt = u"'replace': 'This text is a replacement'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)


    def test_static_processor_wrong_x_path(self):
        self.setUpProcessorTest()
        self.se_title.x_path = u'/div[@class="class_which_is_not_there"]/text()'
        self.se_title.processors = u'static'
        self.se_title.proc_ctxt = u"'static': 'This text should always be there'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)


    def test_static_processor_correct_x_path(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'static'
        self.se_title.proc_ctxt = u"'static': 'This text should always be there'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)  
    
    
    def test_reg_exp(self):
        self.se_desc.reg_exp = u'(\d{6})'
        self.se_desc.save()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_reg_exp/event_main.html')
        self.event_website.save()
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
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_imgs/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(Event.objects.get(title='Event 1').description, '1d7c0c2ea752d7aa951e88f2bc90a3f17058c473.jpg')
        self.assertTrue(os.access(path1, os.F_OK))
        self.assertTrue(os.access(path2, os.F_OK))
    
    
    def test_missing_img_when_img_field_not_mandatory(self):
        self.se_desc.mandatory = False
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_imgs/event_main2.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 1)

        