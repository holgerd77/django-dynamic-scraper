import os.path

from django.test import TestCase

from scrapy import signals
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher

from dynamic_scraper.spiders.django_spider import DjangoSpider
from dynamic_scraper.spiders.django_checker import DjangoChecker
from dynamic_scraper.spiders.checker_test import CheckerTest
from dynamic_scraper.models import *
from scraper.models import EventWebsite, Event, EventItem


# Tests need webserver for serving test pages: python manage.py runserver 0.0.0.0:8010


class EventSpider(DjangoSpider):
    
    name = 'event_spider'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(EventWebsite, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Event
        self.scraped_obj_item_class = EventItem
        super(EventSpider, self).__init__(self, *args, **kwargs)


class DjangoWriterPipeline(object):
    
    def process_item(self, item, spider):
        item['event_website'] = spider.ref_object
        
        checker_rt = SchedulerRuntime()
        checker_rt.save()
        item['checker_runtime'] = checker_rt
        
        if not 'description' in item or item['description'] == None:
            item['description'] = u''
        
        item.save()
        return item 


class EventChecker(DjangoChecker):
    
    name = 'event_checker'
    
    def __init__(self, *args, **kwargs):
        self._set_ref_object(Event, **kwargs)
        self.scraper = self.ref_object.event_website.scraper
        self.scrape_url = self.ref_object.url
        self.scheduler_runtime = self.ref_object.checker_runtime
        super(EventChecker, self).__init__(self, *args, **kwargs)


class ScraperTest(TestCase):

    SERVER_URL = 'http://localhost:8010/static/'
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    

    def record_signal(self, *args, **kwargs):
        pass
        #print kwargs
    

    def run_event_spider(self, id, do_action='yes'):
        kwargs = {
        'id': id,
        'do_action': do_action,
        }
        self.spider = EventSpider(**kwargs)
        self.crawler.crawl(self.spider)
        self.crawler.start()
        
    
    def run_event_checker(self, id):
        kwargs = {
        'id': id,
        'do_action': 'yes'
        }
        self.checker = EventChecker(**kwargs)
        self.crawler.crawl(self.checker)
        self.crawler.start()
    
    
    def run_checker_test(self, id):
        kwargs = {
        'id': id,
        }
        self.checker_test = CheckerTest(**kwargs)
        self.checker_test.conf['RUN_TYPE'] = 'TASK'
        self.checker_test.conf['DO_ACTION'] = True
        self.checker_test.conf['LOG_ENABLED'] = True
        self.checker_test.conf['LOG_LEVEL'] = 'DEBUG' 
        self.crawler.crawl(self.checker_test)
        self.crawler.start()
    
    
    def setUp(self):        
        self.sc = ScrapedObjClass(name='Event')
        self.sc.save()
        self.soa_base = ScrapedObjAttr(name=u'base', attr_type='B', obj_class=self.sc)
        self.soa_base.save()
        self.soa_title = ScrapedObjAttr(name=u'title', attr_type='S', obj_class=self.sc)
        self.soa_title.save()
        self.soa_url = ScrapedObjAttr(name=u'url', attr_type='U', obj_class=self.sc)
        self.soa_url.save()
        self.soa_desc = ScrapedObjAttr(name=u'description', attr_type='S', obj_class=self.sc)
        self.soa_desc.save()

        self.scraper = Scraper(name=u'Event Scraper', scraped_obj_class=self.sc, status='A',)
        self.scraper.save()
        
        self.se_base = ScraperElem(scraped_obj_attr=self.soa_base, scraper=self.scraper, 
        x_path=u'//ul/li', from_detail_page=False)
        self.se_base.save()
        self.se_title = ScraperElem(scraped_obj_attr=self.soa_title, scraper=self.scraper, 
            x_path=u'a/text()', from_detail_page=False)
        self.se_title.save()
        self.se_url = ScraperElem(scraped_obj_attr=self.soa_url, scraper=self.scraper, 
            x_path=u'a/@href', from_detail_page=False)
        self.se_url.save()
        self.se_desc = ScraperElem(scraped_obj_attr=self.soa_desc, scraper=self.scraper, 
            x_path=u'//div/div[@class="description"]/text()', from_detail_page=True, mandatory=False)
        self.se_desc.save()
        
        self.sched_rt = SchedulerRuntime()
        self.sched_rt.save()
        
        self.event_website = EventWebsite(pk=1, name=u'Event Website', scraper=self.scraper,
            url=os.path.join(self.SERVER_URL, 'site_generic/event_main.html'), scraper_runtime=self.sched_rt,)
        self.event_website.save()
        
        
        settings.overrides['ITEM_PIPELINES'] = [
            'dynamic_scraper.pipelines.DjangoImagesPipeline',
            'dynamic_scraper.pipelines.ValidationPipeline',
            'scraper.scraper_test.DjangoWriterPipeline',
        ]
        
        settings.overrides['IMAGES_STORE'] = os.path.join(self.PROJECT_ROOT, 'imgs')
        settings.overrides['IMAGES_THUMBS'] = { 'small': (170, 170), }
        
        self.crawler = CrawlerProcess(settings)
        self.crawler.install()
        self.crawler.configure()
        
        for name, signal in vars(signals).items():
            if not name.startswith('_'):
                dispatcher.connect(self.record_signal, signal)
        
    
    def tearDown(self):
        pass
        

        
    