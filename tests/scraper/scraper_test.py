import os, os.path, shutil

from django.test import TestCase

from scrapy import log, signals

from scrapy.utils.project import get_project_settings
settings = get_project_settings()

from twisted.internet import reactor
from scrapy.crawler import Crawler
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
    IMG_DIR = './scraper/imgs/'

    def __init__(self, *args, **kwargs):
        if args[0] == 'test_img_store_format_flat_with_thumbs' or args[0] == 'test_delete_with_img_flat_with_thumbs':
            os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings.images_store_format_flat_with_thumbs';
            from settings import images_store_format_flat_with_thumbs as file_settings
        elif args[0] == 'test_img_store_format_all_no_thumbs' or args[0] == 'test_delete_with_img_all_no_thumbs':
            os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings.images_store_format_all_no_thumbs';
            from settings import images_store_format_all_no_thumbs as file_settings
        elif args[0] == 'test_img_store_format_all_with_thumbs' or args[0] == 'test_delete_with_img_all_with_thumbs':
            os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings.images_store_format_all_with_thumbs';
            from settings import images_store_format_all_with_thumbs as file_settings
        elif args[0] == 'test_img_store_format_thumbs_with_thumbs' or args[0] == 'test_delete_with_img_thumbs_with_thumbs':
            os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings.images_store_format_thumbs_with_thumbs';
            from settings import images_store_format_thumbs_with_thumbs as file_settings
        else:
            os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings.base_settings';
            from settings import base_settings as file_settings
        
        self.dds_settings = {}
        self.dds_settings['ITEM_PIPELINES'] = file_settings.ITEM_PIPELINES
        self.dds_settings['SPLASH_URL'] = file_settings.SPLASH_URL
        self.dds_settings['DUPEFILTER_CLASS'] = file_settings.DUPEFILTER_CLASS
        self.dds_settings['DOWNLOADER_MIDDLEWARES'] = file_settings.DOWNLOADER_MIDDLEWARES
        self.dds_settings['DSCRAPER_SPLASH_ARGS'] = file_settings.DSCRAPER_SPLASH_ARGS
        self.dds_settings['IMAGES_STORE'] = file_settings.IMAGES_STORE
        if 'IMAGES_THUMBS' in file_settings.__dict__:
            self.dds_settings['IMAGES_THUMBS'] = file_settings.IMAGES_THUMBS
        if 'DSCRAPER_IMAGES_STORE_FORMAT' in file_settings.__dict__:
            self.dds_settings['DSCRAPER_IMAGES_STORE_FORMAT'] = file_settings.DSCRAPER_IMAGES_STORE_FORMAT

        super(ScraperTest, self).__init__(*args, **kwargs)


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
        #log.start(loglevel="DEBUG", logstdout=True)
        reactor.run()
        
    
    def run_event_checker(self, id):
        kwargs = {
        'id': id,
        'do_action': 'yes'
        }
        self.checker = EventChecker(**kwargs)
        self.crawler.crawl(self.checker)
        self.crawler.start()
        #log.start(loglevel="DEBUG", logstdout=True)
        reactor.run()
    
    
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
        log.start(loglevel="DEBUG", logstdout=True)
        reactor.run()
    
    
    def setUp(self):
        if os.path.exists(self.IMG_DIR):
            shutil.rmtree(self.IMG_DIR)
        os.mkdir(self.IMG_DIR)

        settings.set('ITEM_PIPELINES', self.dds_settings['ITEM_PIPELINES'], priority='cmdline')
        settings.set('SPLASH_URL', self.dds_settings['SPLASH_URL'], priority='cmdline')
        settings.set('DUPEFILTER_CLASS', self.dds_settings['DUPEFILTER_CLASS'], priority='cmdline')
        settings.set('DOWNLOADER_MIDDLEWARES', self.dds_settings['DOWNLOADER_MIDDLEWARES'], priority='cmdline')
        settings.set('IMAGES_STORE', self.dds_settings['IMAGES_STORE'], priority='cmdline')
        if 'IMAGES_THUMBS' in self.dds_settings:
            settings.set('IMAGES_THUMBS', self.dds_settings['IMAGES_THUMBS'], priority='cmdline')
        if 'DSCRAPER_IMAGES_STORE_FORMAT' in self.dds_settings:
            settings.set('DSCRAPER_IMAGES_STORE_FORMAT', self.dds_settings['DSCRAPER_IMAGES_STORE_FORMAT'], priority='cmdline')

        settings.set('COOKIES_DEBUG', True)
        self.crawler = Crawler(settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.crawler.configure()

        self.sc = ScrapedObjClass(name='Event')
        self.sc.save()
        self.soa_base = ScrapedObjAttr(name=u'base', attr_type='B', obj_class=self.sc)
        self.soa_base.save()
        self.soa_title = ScrapedObjAttr(name=u'title', attr_type='S', obj_class=self.sc)
        self.soa_title.save()
        self.soa_url = ScrapedObjAttr(name=u'url', attr_type='U', obj_class=self.sc, id_field=True)
        self.soa_url.save()
        self.soa_url2 = ScrapedObjAttr(name=u'url2', attr_type='U', obj_class=self.sc)
        self.soa_url2.save()
        self.soa_desc = ScrapedObjAttr(name=u'description', attr_type='S', obj_class=self.sc)
        self.soa_desc.save()
        self.soa_desc2 = ScrapedObjAttr(name=u'description2', attr_type='S', obj_class=self.sc)
        self.soa_desc2.save()

        self.scraper = Scraper(name=u'Event Scraper', scraped_obj_class=self.sc, status='A',)
        self.scraper.save()
        
        self.se_base = ScraperElem(scraped_obj_attr=self.soa_base, scraper=self.scraper, 
        x_path=u'//ul/li', request_page_type='MP')
        self.se_base.save()
        self.se_title = ScraperElem(scraped_obj_attr=self.soa_title, scraper=self.scraper, 
            x_path=u'a/text()', request_page_type='MP')
        self.se_title.save()
        self.se_url = ScraperElem(scraped_obj_attr=self.soa_url, scraper=self.scraper, 
            x_path=u'a/@href', request_page_type='MP')
        self.se_url.save()
        self.se_desc = ScraperElem(scraped_obj_attr=self.soa_desc, scraper=self.scraper, 
            x_path=u'//div/div[@class="description"]/text()', request_page_type='DP1', mandatory=False)
        self.se_desc.save()

        self.rpt_mp  = RequestPageType(page_type='MP', scraper=self.scraper)
        self.rpt_mp.save()
        self.rpt_dp1 = RequestPageType(page_type='DP1', scraper=self.scraper, scraped_obj_attr=self.soa_url)
        self.rpt_dp1.save()
        
        self.sched_rt = SchedulerRuntime()
        self.sched_rt.save()
        
        self.event_website = EventWebsite(pk=1, name=u'Event Website', scraper=self.scraper,
            url=os.path.join(self.SERVER_URL, 'site_generic/event_main.html'), scraper_runtime=self.sched_rt,)
        self.event_website.save()
        
        for name, signal in vars(signals).items():
            if not name.startswith('_'):
                dispatcher.connect(self.record_signal, signal)
        
    
    def tearDown(self):
        pass
        

        
    