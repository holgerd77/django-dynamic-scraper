import ast

from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.exceptions import CloseSpider

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.scheduler import Scheduler
from dynamic_scraper.utils import processors


class DjangoSpider(DjangoBaseSpider):

    def __init__(self, *args, **kwargs):
        self._set_conf(**kwargs)
        
        if self.scraper_runtime:
            self.scraper = self.scraper_runtime.scraper
            self.scheduler_runtime = self.scraper_runtime.scheduler_runtime
        
        mandatory_vars = [
            'scraped_obj_class',
            'scraped_obj_item_class',
        ]
        self._check_mandatory_vars(mandatory_vars)
        
        self._set_start_urls(self.scraper_runtime.url)
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.scraper_scheduler_conf)
        self._check_scraper_config()
        self.follow_url = False
        self.loader = None
        self.items_read_count = 0
        self.items_save_count = 0


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
        
        if self.scraper.pagination_type != 'N':
            if not self.scraper.pagination_append_str:
                raise CloseSpider('Please provide a pagination_append_str for pagination (e.g. "/archive/{page}/")!')
            if self.scraper.pagination_append_str.find('{page}') == -1:
                raise CloseSpider('Pagination_append_str has to contain "{page}" as placeholder for page replace!')
            if not self.scraper.pagination_page_replace:
                raise CloseSpider('Please provide a pagination_page_replace context corresponding to pagination_type!')
        
        if self.scraper.pagination_type == 'R':
            try:
                pages = self.scraper.pagination_page_replace
                pages = pages.split(',')
                if len(pages) > 3:
                    raise Exception
                pages = range(*map(int, pages)) 
            except Exception:
                raise CloseSpider('Pagination_page_replace for pagination_type "RANGE_FUNCT" ' +\
                                  'has to be provided as python range function arguments ' +\
                                  '[start], stop[, step] (e.g. "1, 50, 10", no brackets)!')
        
        if self.scraper.pagination_type == 'F':
            try:
                pages = self.scraper.pagination_page_replace
                pages = pages.strip(', ')
                pages = ast.literal_eval("[" + pages + ",]")
            except SyntaxError:
                raise CloseSpider('Wrong pagination_page_replace format for pagination_type "FREE_LIST", ' +\
                                  "Syntax: 'Replace string 1', 'Another replace string 2', 'A number 3', ...")
                
        
        
        if self.scraper.pagination_type != 'N':
            append_str = self.scraper.pagination_append_str
            if scrape_url[-1:] == '/' and append_str[0:1] == '/':
                append_str = append_str[1:]

            for page in pages:
                url = scrape_url + append_str.format(page=page)
                self.start_urls.append(url)
            if not self.scraper.pagination_on_start:
                self.start_urls.append(scrape_url)
        
        if self.scraper.pagination_type == 'N':
            self.start_urls.append(scrape_url)


    def _set_loader_context(self, context_str):
        try:
            #add_ctxt1 = "'pre_log_msg': '" + self.pre_log_msg + "'"
            #context_str = ", ".join([context_str, add_ctxt1])
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
            self.items_read_count += 1
            
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
        if(self.scraper.max_items_read):
            items_left = min(len(base_objects), self.scraper.max_items_read - self.items_read_count)
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
                    
    
