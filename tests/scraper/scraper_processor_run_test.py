# -*- coding: utf-8 -*-
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
    
    
    def setUpProcessorTestWithDetailPageUrlPlaceholder(self):
        self.se_url.processors = u'pre_url'
        self.se_url.proc_ctxt = u"'pre_url': 'http://localhost:8010/static/{title}/'"
        self.se_url.save()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_processor/event_main_placeholder.html')
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
    
    
    def test_replace_processor_unicode_replace(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'replace'
        self.se_title.proc_ctxt = u"'replace': 'Replacement with beautiful unicode ❤ ☀ ★ ☂ ☻ ♞ ☯ ☭ ☢'"
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
    
    
    def test_static_processor_empty_x_path(self):
        self.setUpProcessorTest()
        self.se_title.x_path = u''
        self.se_title.processors = u'static'
        self.se_title.proc_ctxt = u"'static': 'This text should always be there'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.filter(title='This text should always be there')), 2)
    

    def test_static_processor_correct_x_path(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'static'
        self.se_title.proc_ctxt = u"'static': 'This text should always be there'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
    
    
    def test_static_processor_unicode_text(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'static'
        self.se_title.proc_ctxt = u"'static': 'This text should always be there ❤ ☀ ★ ☂ ☻ ♞ ☯ ☭ ☢'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.filter(title='This text should always be there ❤ ☀ ★ ☂ ☻ ♞ ☯ ☭ ☢')), 2)
    
    
    def test_reg_exp(self):
        self.se_desc.reg_exp = u'(\d{6})'
        self.se_desc.save()
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_reg_exp/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(Event.objects.get(title='Event 1').description, '563423')
    
    
    def test_processor_with_detail_page_url_placeholder(self):
        self.setUpProcessorTestWithDetailPageUrlPlaceholder()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 1)
        self.assertEqual(
            Event.objects.get(title='site_with_processor').url,
            'http://localhost:8010/static/site_with_processor/event1.html')
    
    
    def test_processor_with_placeholder_mp_to_dp(self):
        self.setUpProcessorTest()
        self.se_desc.processors = u'post_string'
        self.se_desc.proc_ctxt = u"'post_string': '_START_{title}_END'"
        self.se_desc.save()
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.filter(description='Event 1 description_START_Event 1_END').count(), 1)
    
    
    def test_processor_with_placeholder_mp_to_dp_unicode(self):
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_unicode/event_main.html')
        self.event_website.save()
        self.se_desc.processors = u'post_string'
        self.se_desc.proc_ctxt = u"'post_string': '_START_{title}_END'"
        self.se_desc.save()
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.filter(description='Event 1 description ♖ ☦ ✝ ❖ ➎ ♠ ♣ ♥_START_Event 1 ❤ ☀ ★ ☂ ☻ ♞ ☯ ☭ ☢_END').count(), 1)
    
    
    def test_processor_with_placeholder_dp_to_mp(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'post_string'
        self.se_title.proc_ctxt = u"'post_string': '_START_{description}_END'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.filter(title='Event 1_START_Event 1 description_END').count(), 1)
    
    
    def test_processor_with_placeholder_tmp_to_mp(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'post_string'
        self.se_title.proc_ctxt = u"'post_string': '_START_{extra_standard_1}_END'"
        self.se_title.save()
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.filter(title='Event 1_START_Event 1_END').count(), 1)
    
    
    def test_processor_with_placeholder_tmp_with_placeholder_to_mp(self):
        self.setUpProcessorTest()
        self.se_title.processors = u'post_string'
        self.se_title.proc_ctxt = u"'post_string': '_START_{extra_standard_1}_END'"
        self.se_title.save()
        self.se_es_1.processors = u'remove_chars'
        self.se_es_1.proc_ctxt = u"'remove_chars': '[0-9 ]+'"
        self.se_es_1.save()
        self.run_event_spider(1)
        
        self.assertEqual(Event.objects.filter(title='Event 1_START_Event_END').count(), 1)
        
        