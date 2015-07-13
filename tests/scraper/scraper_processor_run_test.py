import os.path, unittest

from twisted.internet import reactor
from scrapy import log
from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime, Log


class ScraperProcessorRunTest(ScraperTest):

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
    
    
    @unittest.skip("Skipped due to unresolved problem that order of processor execution can not clearly determined.")
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