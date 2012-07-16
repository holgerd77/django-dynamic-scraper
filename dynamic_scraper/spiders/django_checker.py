import os
from scrapy import log, signals
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.xlib.pydispatch import dispatcher

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.scheduler import Scheduler


class DjangoChecker(DjangoBaseSpider):
    
    name = "django_checker"


    def __init__(self, *args, **kwargs):
        super(DjangoChecker, self).__init__(self, *args, **kwargs)
        self._set_config(**kwargs)
        self._check_checker_config()
        
        self.start_urls.append(self.scrape_url)
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.checker_scheduler_conf)
        dispatcher.connect(self.response_received, signal=signals.response_received)
        
        msg = "Checker for " + self.ref_object.__class__.__name__ + " \"" + str(self.ref_object) + "\" (" + str(self.ref_object.id) + ") initialized."
        self.log(msg, log.INFO)

    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(DjangoChecker, self)._set_config(log_msg, **kwargs)


    def _check_checker_config(self):
        if self.scraper.checker_type == 'N':
            msg = 'No checker defined for scraper!'
            log.msg(msg, log.WARNING)
            raise CloseSpider(msg)


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
            
            if self.scheduler_runtime.num_zero_actions == 0:
                self.log("Checker test returned second 404.", log.INFO)
                if self.conf['DO_ACTION']:
                    self._del_ref_object()
            else:
                self.log("Checker test returned first 404.", log.INFO)
                self.action_successful = True


    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # x_path test
        if self.scraper.checker_type == '4':
            self.log("No 404. Item kept.", log.INFO)
            return
        try:
            test_select = hxs.select(self.scraper.checker_x_path).extract()
        except ValueError:
            self.log('Invalid checker x_path!', log.ERROR)
            return
        if len(test_select) > 0 and test_select[0] == self.scraper.checker_x_path_result:
            self.log("XPath result string '" + self.scraper.checker_x_path_result + "' found on page.", log.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
        else:
            self.log("XPath result string not found. Item kept.", log.INFO)
            return
