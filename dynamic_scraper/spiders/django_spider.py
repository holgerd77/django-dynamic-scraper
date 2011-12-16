import ast

from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.exceptions import CloseSpider

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem, SchedulerRuntime
from dynamic_scraper.utils.scheduler import Scheduler
from dynamic_scraper.utils import processors


class DjangoSpider(DjangoBaseSpider):

    def __init__(self, *args, **kwargs):
        mandatory_vars = [
            'scraper',
            'scraper_runtime',
            'scraped_obj_class',
            'scraped_obj_item_class',
        ]
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.scraper_scheduler_conf)
        self.scheduler_runtime = self.scraper_runtime.scheduler_runtime
        self._check_mandatory_vars(mandatory_vars)
        self._check_scraper_config()
        self.follow_url = False
        self.loader = None
        self.item_count = 0
        self._set_conf(**kwargs)


    def _check_scraper_config(self):
        try:
            self.scraper.get_base_elem() 
        except ScraperElem.DoesNotExist:
            raise CloseSpider('Please define a base scraper elem in your database!')
        try:
            self.scraper.get_follow_url_elem() 
        except ScraperElem.DoesNotExist:
            raise CloseSpider('Please define a url scraper elem in your database!')
        if(len(self.scraper.get_base_elems()) > 1):
            raise CloseSpider('A scraper can\'t have more than one base scraper elem!')
        if(len(self.scraper.get_follow_url_elems()) > 1):
            raise CloseSpider('A scraper can\'t have more than one url scraper elem!')


    def _set_start_urls(self, scrape_url):
        
        if not hasattr(self, 'scraper'):
            raise CloseSpider('Please provide a scraper before calling this method!')
        
        if self.scraper.use_pagination:
            if not self.scraper.pagination_append_str:
                raise CloseSpider('Please provide a pagination_append_str for pagination (e.g. "/archive/{page}/")!')
            if self.scraper.pagination_append_str.find('{page}') == -1:
                raise CloseSpider('Pagination_append_str has to contain "{page}" as placeholder for page number')
            if not self.scraper.pagination_range:
                raise CloseSpider('Please provide a pagination_range for pagination (e.g. "1, 10")!')
            try:
                p_range = self.scraper.pagination_range
                p_range = p_range.split(',')
                if len(p_range) > 3:
                    raise Exception
                p_range = range(*map(int, p_range)) 
            except Exception:
                raise CloseSpider('Pagination_range has to be provided as python range function arguments ' +\
                    '[start], stop[, step] (e.g. "1, 50, 10", no brackets)!')
            append_str = self.scraper.pagination_append_str
            if scrape_url[-1:] == '/' and append_str[0:1] == '/':
                append_str = append_str[1:]

            for page in p_range:
                url = scrape_url + append_str.format(page=page)
                self.start_urls.append(url)
            if not self.scraper.pagination_on_start:
                self.start_urls.append(scrape_url)
        else:
            self.start_urls.append(scrape_url)
        

    def log(self, message, level=log.DEBUG):
        
        if(level == log.CRITICAL):
            self.scraper_runtime.num_criticals += 1
            self.scraper_runtime.last_critical_msg = message
        if(level == log.ERROR):
            self.scraper_runtime.num_errors += 1
            self.scraper_runtime.last_error_msg = message
        if(level == log.WARNING):
            self.scraper_runtime.num_warnings += 1
            self.scraper_runtime.last_warning_msg = message
            
        super(DjangoSpider, self).log(message, level)


    def _set_loader_context(self, context_str):
        try:
            add_ctxt1 = "'pre_log_msg': '" + self.pre_log_msg + "'"
            context_str = ", ".join([context_str, add_ctxt1])
            context_str = context_str.strip(', ')
            context = ast.literal_eval("{" + context_str + "}")
            self.loader.context = context
        except SyntaxError:
            self.log("Wrong context definition format: " + context_str, log.ERROR)


    def _get_processors(self, procs_str):
        procs_tmp = list(procs_str.split(','))
        procs = [TakeFirst(), processors.string_strip,]
        for p in procs_tmp:
            if(hasattr(processors, p)):
                procs.append(getattr(processors, p))
        procs = tuple(procs)
        return procs


    def _scrape_item_attr(self, scraper_elem):
        if(self.follow_url == scraper_elem.follow_url):
            procs = self._get_processors(scraper_elem.processors)
            self._set_loader_context(scraper_elem.proc_ctxt)
            if(scraper_elem.reg_exp):
                self.loader.add_xpath(scraper_elem.scraped_obj_attr.name, scraper_elem.x_path, *procs,  re=scraper_elem.reg_exp)
            else:
                self.loader.add_xpath(scraper_elem.scraped_obj_attr.name, scraper_elem.x_path, *procs)


    def _set_loader(self, response, hxs, item):
        if not hxs:
            self.follow_url = True
            item = response.request.meta['item']
            self.loader = XPathItemLoader(item=item, response=response)
            self.loader.default_output_processor = TakeFirst()
        else:
            self.follow_url = False
            self.loader = XPathItemLoader(item=item, selector=hxs)
            self.loader.default_output_processor = TakeFirst()


    def parse_item(self, response, hxs=None):
        self._set_loader(response, hxs, self.scraped_obj_item_class())
        if not self.follow_url:
            check_rt = SchedulerRuntime()
            check_rt.save()
            self.loader.add_value('checker_runtime', check_rt)
            self.item_count += 1
            
        elems = self.scraper.get_scrape_elems()
        for elem in elems:
            self._scrape_item_attr(elem)
        
        return self.loader.load_item()


    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        base_elem = self.scraper.get_base_elem()
        url_elem = self.scraper.get_follow_url_elem()
        base_objects = hxs.select(base_elem.x_path)
        if(len(base_objects) == 0):
            self.log("No base objects found!", log.ERROR)
        if(self.scraper.max_items):
            items_left = min(len(base_objects), self.scraper.max_items - self.item_count)
            base_objects = base_objects[0:items_left]
        
        for obj in base_objects:
            item = self.parse_item(response, obj)
            #print item
            url_name = url_elem.scraped_obj_attr.name
            if(item and url_name in item):
                cnt = self.scraped_obj_class.objects.filter(url=item[url_name]).count()
                # Check for double items
                if(cnt > 0):
                    item[url_name] = 'DOUBLE'
                else:
                    yield Request(item[url_name], callback=self.parse_item, meta={'item':item})
                    
    
