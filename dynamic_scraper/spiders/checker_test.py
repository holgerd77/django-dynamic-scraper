#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from builtins import str
import logging
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from pydispatch import dispatcher
from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import Scraper


class CheckerTest(DjangoBaseSpider):
    
    name = 'checker_test'
    mandatory_vars = ['ref_object', 'scraper',]
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        
        spider._set_ref_object(Scraper, **kwargs)
        spider.scraper = spider.ref_object
        spider._set_config(**kwargs)
        
        if spider.scraper.checker_set.count() == 0:
            msg = "No checkers defined for scraper!"
            spider.dds_logger.error(msg)
            raise CloseSpider(msg)
        
        for checker in spider.scraper.checker_set.all():
            if checker.checker_type == '4':
                if not checker.checker_ref_url:
                    msg = "Please provide a reference url for your checker ({c}).".format(c=str(checker))
                    spider.dds_logger.error(msg)
                    raise CloseSpider(msg)
            
            if checker.checker_type == 'X':
                if not checker.checker_x_path or not checker.checker_ref_url:
                    msg = "Please provide the necessary x_path fields for your checker ({c}).".format(c=str(checker))
                    spider.dds_logger.error(msg)
                    raise CloseSpider(msg)

        spider._set_request_kwargs()
        spider._set_meta_splash_args()
        
        dispatcher.connect(spider.response_received, signal=signals.response_received)
        
        return spider
    
    
    def output_usage_help(self):
        out = (
            '',
            'DDS Usage',
            '=========',
            '  scrapy crawl [scrapy_options] checker_test -a id=SCRAPER_ID [dds_options]',
            '',
            'Options',
            '-------',
            '-L LOG_LEVEL (scrapy option)            Setting the log level for both Scrapy and DDS',
            '-a output_response_body=(yes|no)        Output response body content for debugging',
            '',
        )
        for out_str in out:
            self.dds_logger.info(out_str)
    
    
    def _set_config(self, **kwargs):
        log_msg = ""
        #output_response_body
        if 'output_response_body' in kwargs and kwargs['output_response_body'] == 'yes':
            self.conf['OUTPUT_RESPONSE_BODY'] = True
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "output_response_body " + str(self.conf['OUTPUT_RESPONSE_BODY'])
        else:
            self.conf['OUTPUT_RESPONSE_BODY'] = False
        
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
                self.log("{cs}Checker configuration working (ref url request returning 404) ({c}).{ce}".format(c=str(checker), cs=self.bcolors['OK'], ce=self.bcolors['ENDC']), logging.INFO)
            if checker.checker_type == 'X':
                self.log('{cs}A request of your checker ref url is returning 404. Your x_path can not be applied ({c}).{ce}'.format(
                    c=str(checker), cs=self.bcolors['INFO'], ce=self.bcolors['ENDC']), logging.WARNING)
        else:
            if checker.checker_type == '4':
                self.log('Checker ref url request not returning 404 ({c})!'.format(c=str(checker)), logging.WARNING)
    
    
    def parse(self, response):        
        checker = response.request.meta['checker']
        rpt = response.request.meta['rpt']
        
        if self.conf['OUTPUT_RESPONSE_BODY']:
            self.log("Response body ({url})\n\n***** RP_START *****\n{resp_body}\n***** RP_END *****\n\n".format(
                url=response.url,
                resp_body=response.body.decode('utf-8')), logging.INFO)
        
        if checker.checker_type == '4':
            return
        
        try:
            test_select = response.xpath(checker.checker_x_path).extract()
        except ValueError:
            self.log('Invalid x_path ({c})!'.format(c=str(checker)), logging.ERROR)
            return
        if len(test_select) == 0:
            self.log("{cs}Checker configuration not working (no elements found for xpath on reference url page) ({c})!{ce}".format(
                c=str(checker), cs=self.bcolors['ERROR'], ce=self.bcolors['ENDC']), logging.ERROR)
        else:
            if checker.checker_x_path_result == '':
                self.log("{cs}Checker configuration working (elements for x_path found on reference url page (no x_path result defined)) ({c}).{ce}".format(
                    c=str(checker), cs=self.bcolors['OK'], ce=self.bcolors['ENDC']), logging.INFO)
            else:
                if test_select[0] != checker.checker_x_path_result:
                    self.log("{cs}Checker configuration not working (expected x_path result not found on reference url page) ({c})!{ce}".format(
                        c=str(checker), cs=self.bcolors['ERROR'], ce=self.bcolors['ENDC']), logging.ERROR)
                else:
                    self.log("{cs}Checker configuration working (expected x_path result found on reference url page) ({c}).{ce}".format(
                        c=str(checker), cs=self.bcolors['OK'], ce=self.bcolors['ENDC']), logging.INFO)
                
        