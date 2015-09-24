from scrapy import log, signals
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import Scraper


class CheckerTest(DjangoBaseSpider):
    
    name = 'checker_test'
    
    command = 'scrapy crawl checker_test -a id=SCRAPER_ID'
    
    def __init__(self, *args, **kwargs):
        self._set_ref_object(Scraper, **kwargs)
        self.scraper = self.ref_object
        self._set_config(**kwargs)
        
        if self.scraper.checker_type == 'N':
            msg = "No checker defined for scraper!"
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)
        
        if self.scraper.get_detail_page_url_id_elems().count() != 1:
            msg = 'Checkers can only be used for scraped object classed defined with a single DETAIL_PAGE_URL type id field!'
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)
        
        if self.scraper.checker_type == '4':
            if not self.scraper.checker_ref_url:
                msg = "Please provide a reference url for your 404 checker (Command: %s)." % (self.command)
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)
        
        if self.scraper.checker_type == 'X':
            if not self.scraper.checker_x_path or not self.scraper.checker_ref_url:
                msg = "Please provide the necessary x_path fields for your 404_OR_X_PATH checker (Command: %s)." % (self.command)
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)

        self._set_request_kwargs()
        self._set_meta_splash_args()
        
        self.start_urls.append(self.scraper.checker_ref_url)
        dispatcher.connect(self.response_received, signal=signals.response_received)
    
    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(CheckerTest, self)._set_config(log_msg, **kwargs)
    
    
    def spider_closed(self):
        pass
    
    
    def start_requests(self):
        for url in self.start_urls:
            url_elem = self.scraper.get_detail_page_url_id_elems()[0]
            self.rpt = self.scraper.get_rpt_for_scraped_obj_attr(url_elem.scraped_obj_attr)
            kwargs = self.dp_request_kwargs[self.rpt.page_type].copy()
            self._set_meta_splash_args()

            if self.rpt.request_type == 'R':
                yield Request(url, callback=self.parse, method=self.rpt.method, dont_filter=self.rpt.dont_filter, **kwargs)
            else:
                yield FormRequest(url, callback=self.parse, method=self.rpt.method, formdata=self.dp_form_data[self.rpt.page_type], dont_filter=self.rpt.dont_filter, **kwargs)


    def response_received(self, **kwargs):
        if kwargs['response'].status == 404:
            if self.scraper.checker_type == '4':
                self.log("Checker configuration working (ref url request returning 404).", log.INFO)
            if self.scraper.checker_type == 'X':
                self.log('A request of your ref url is returning 404. Your x_path can not be applied!', log.WARNING)
        else:
            if self.scraper.checker_type == '4':
                self.log('Ref url request not returning 404!', log.WARNING)
    
    def parse(self, response):        
        if self.scraper.checker_type == '4':
            return

        try:
            test_select = response.xpath(self.scraper.checker_x_path).extract()
        except ValueError:
            self.log('Invalid checker x_path!', log.ERROR)
            return
        if len(test_select) == 0:
            self.log("Checker configuration not working (no elements found for xpath on reference url page)!", log.ERROR)
        else:
            if self.scraper.checker_x_path_result == '':
                self.log("Checker configuration working (elements for x_path found on reference url page (no x_path result defined)).", log.INFO)
            else:
                if test_select[0] != self.scraper.checker_x_path_result:
                    self.log("Checker configuration not working (expected x_path result not found on reference url page)!", log.ERROR)
                else:
                    self.log("Checker configuration working (expected x_path result found on reference url page).", log.INFO)
                
        