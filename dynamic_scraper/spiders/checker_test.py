from scrapy import log, signals
from scrapy.exceptions import CloseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.xlib.pydispatch import dispatcher
from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import Scraper


class CheckerTest(DjangoBaseSpider):
    
    name = 'checker_test'
    
    command = 'scrapy crawl checker_test -a id=SCRAPER_ID'
    
    def __init__(self, *args, **kwargs):
        self._set_ref_object(Scraper, **kwargs)
        self._set_config(**kwargs)
        
        if self.ref_object.checker_type == 'N':
            msg = "No checker defined for scraper!"
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)
        
        if self.ref_object.checker_type == '4':
            if not self.ref_object.checker_ref_url:
                msg = "Please provide a reference url for your 404 checker (Command: %s)." % (self.command)
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)
        
        if self.ref_object.checker_type == 'X':
            if not self.ref_object.checker_x_path or not self.ref_object.checker_x_path_result or not self.ref_object.checker_ref_url:
                msg = "Please provide the necessary x_path fields for your 404_OR_X_PATH checker (Command: %s)." % (self.command)
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)
        
        self.start_urls.append(self.ref_object.checker_ref_url)
        dispatcher.connect(self.response_received, signal=signals.response_received)
    
    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(CheckerTest, self)._set_config(log_msg, **kwargs)
    
    
    def spider_closed(self):
        pass
    
    
    def response_received(self, **kwargs):
        if kwargs['response'].status == 404:
            if self.ref_object.checker_type == '4':
                self.log("Checker configuration working (ref url request returning 404).", log.INFO)
            if self.ref_object.checker_type == 'X':
                self.log('A request of your ref url is returning 404. Your x_path can not be applied!', log.WARNING)
        else:
            if self.ref_object.checker_type == '4':
                self.log('Ref url request not returning 404!', log.WARNING)
    
    def parse(self, response):        
        if self.ref_object.checker_type == '4':
            return
        
        hxs = HtmlXPathSelector(response)
        
        try:
            test_select = hxs.select(self.ref_object.checker_x_path).extract()
        except ValueError:
            self.log('Invalid checker x_path!', log.ERROR)
            return
        if len(test_select) == 0 or (len(test_select) > 0 and test_select[0] != self.ref_object.checker_x_path_result):
            self.log("Checker configuration not working (expected x_path result not found on reference url page)!", log.ERROR)
        else:
            self.log("Checker configuration working (expected x_path found on reference url page).", log.INFO)
        