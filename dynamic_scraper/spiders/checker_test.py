from scrapy import log, signals
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import Scraper


class CheckerTest(DjangoBaseSpider):
    
    name = 'checker_test'
    mandatory_vars = ['ref_object', 'scraper',]
    
    command = 'scrapy crawl checker_test -a id=SCRAPER_ID'
    
    def __init__(self, *args, **kwargs):
        self._set_ref_object(Scraper, **kwargs)
        self.scraper = self.ref_object
        self._set_config(**kwargs)
        
        if self.scraper.checker_set.count() == 0:
            msg = "No checkers defined for scraper!"
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)
        
        for checker in self.scraper.checker_set.all():
            if checker.checker_type == '4':
                if not checker.checker_ref_url:
                    msg = "Please provide a reference url for your checker (%s) (Command: %s)." % (unicode(checker), self.command)
                    log.msg(msg, log.ERROR)
                    raise CloseSpider(msg)
            
            if checker.checker_type == 'X':
                if not checker.checker_x_path or not checker.checker_ref_url:
                    msg = "Please provide the necessary x_path fields for your checker (%s) (Command: %s)." % (unicode(checker), self.command)
                    log.msg(msg, log.ERROR)
                    raise CloseSpider(msg)

        self._set_request_kwargs()
        self._set_meta_splash_args()
        
        dispatcher.connect(self.response_received, signal=signals.response_received)
    
    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(CheckerTest, self)._set_config(log_msg, **kwargs)
    
    
    def spider_closed(self):
        pass
    
    
    def start_requests(self):
        for checker in self.scraper.checker_set.all():
            url = checker.checker_ref_url
            rpt = self.scraper.get_rpt_for_scraped_obj_attr(checker.scraped_obj_attr)
            kwargs = self.dp_request_kwargs[rpt.page_type].copy()
            if 'meta' not in kwargs:
                kwargs['meta'] = {}
            kwargs['meta']['checker'] = checker
            kwargs['meta']['rpt'] = rpt
            self._set_meta_splash_args()
            if url:
                if rpt.request_type == 'R':
                    yield Request(url, callback=self.parse, method=rpt.method, dont_filter=True, **kwargs)
                else:
                    yield FormRequest(url, callback=self.parse, method=rpt.method, formdata=self.dp_form_data[rpt.page_type], dont_filter=True, **kwargs)


    def response_received(self, **kwargs):
        checker = kwargs['response'].request.meta['checker']
        rpt = kwargs['response'].request.meta['rpt']
        if kwargs['response'].status == 404:
            if checker.checker_type == '4':
                self.log("Checker configuration working (ref url request returning 404) (%s)." % unicode(checker), log.INFO)
            if checker.checker_type == 'X':
                self.log('A request of your checker ref url is returning 404. Your x_path can not be applied (%s)!' % unicode(checker), log.WARNING)
        else:
            if checker.checker_type == '4':
                self.log('Checker ref url request not returning 404 (%s)!' % unicode(checker), log.WARNING)
    
    
    def parse(self, response):        
        checker = response.request.meta['checker']
        rpt = response.request.meta['rpt']
        
        if checker.checker_type == '4':
            return
        
        try:
            test_select = response.xpath(checker.checker_x_path).extract()
        except ValueError:
            self.log('Invalid x_path (%s)!' % unicode(checker), log.ERROR)
            return
        if len(test_select) == 0:
            self.log("Checker configuration not working (no elements found for xpath on reference url page) (%s)!" % unicode(checker), log.ERROR)
        else:
            if checker.checker_x_path_result == '':
                self.log("Checker configuration working (elements for x_path found on reference url page (no x_path result defined)) (%s)." % unicode(checker), log.INFO)
            else:
                if test_select[0] != checker.checker_x_path_result:
                    self.log("Checker configuration not working (expected x_path result not found on reference url page) (%s)!" % unicode(checker), log.ERROR)
                else:
                    self.log("Checker configuration working (expected x_path result found on reference url page) (%s)." % unicode(checker), log.INFO)
                
        