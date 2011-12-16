import os
from scrapy import log, signals
from scrapy.conf import settings
from scrapy.selector import HtmlXPathSelector
from scrapy.xlib.pydispatch import dispatcher

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.scheduler import Scheduler


class DjangoChecker(DjangoBaseSpider):
    
    name = "django_checker"

    '''
        Load scraped object
        Make x_path test, 404 test
        if(failed): Delete item
        else: Set next check time via scheduler and scraper settings
        That's all! :-) 
    '''

    def __init__(self, *args, **kwargs):
        mandatory_vars = [
            'ref_object',
            'scraper',
            'check_url',
        ]
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.scraper_scheduler_conf)
        self._check_mandatory_vars(mandatory_vars)
        self.start_urls.append(self.check_url)
        self._set_conf(**kwargs)
        dispatcher.connect(self.response_received, signal=signals.response_received)

    
    def _del_ref_object(self):
        try:
            img_elem = self.scraper.get_image_elem()
            if hasattr(self.ref_object, img_elem.scraped_obj_attr.name):
                img_name = getattr(self.ref_object, img_elem.scraped_obj_attr.name)
                path = os.path.join(settings.get('IMAGES_STORE'), img_name)
                if os.access(path, os.F_OK):
                    try:
                        os.unlink(path)
                        self.log("Associated image deleted.", log.INFO)
                    except Exception:
                        self.log("Associated image could not be deleted!", log.ERROR)
        except ScraperElem.DoesNotExist:
            pass
        
        self.ref_object.delete()
        self.action_successful = True
        self.log("Item deleted.", log.INFO)


    def response_received(self, **kwargs):
        # 404 test
        if kwargs['response'].status == 404:
            self.log("Checker test returned 404.", log.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
        

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
            
        # x_path test
        try:
            test_select = hxs.select(self.scraper.checker_x_path).extract()
            if len(test_select) == 0:
                return
            test_select = test_select[0]
        except ValueError:
            self.log('Invalid checker x_path!', log.ERROR)
            return
        if test_select == self.scraper.checker_x_path_result:
            self.log("XPath result string '" + self.scraper.checker_x_path_result + "' found on page.", log.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
