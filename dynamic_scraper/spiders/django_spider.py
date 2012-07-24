import ast

from scrapy import log
from scrapy.selector import HtmlXPathSelector, XmlXPathSelector
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
        self.mandatory_vars.append('scraped_obj_class')
        self.mandatory_vars.append('scraped_obj_item_class')
        
        super(DjangoSpider, self).__init__(self, *args, **kwargs)
        self._set_config(**kwargs)
        self._check_scraper_config()
        
        self._set_start_urls(self.scrape_url)
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.scraper_scheduler_conf)
        self.from_detail_page = False
        self.loader = None
        self.items_read_count = 0
        self.items_save_count = 0
        
        msg = "Spider for " + self.ref_object.__class__.__name__ + " \"" + str(self.ref_object) + "\" (" + str(self.ref_object.id) + ") initialized."
        self.log(msg, log.INFO)


    def _set_config(self, **kwargs):
        log_msg = ""
        #max_items_read 
        if 'max_items_read' in kwargs:
            try:
                self.conf['MAX_ITEMS_READ'] = int(kwargs['max_items_read'])
            except ValueError:
                raise CloseSpider("You have to provide an integer value as max_items_read parameter!")
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "max_items_read " + str(self.conf['MAX_ITEMS_READ'])
        else:
            self.conf['MAX_ITEMS_READ'] = self.scraper.max_items_read
        #max_items_save 
        if 'max_items_save' in kwargs:
            try:
                self.conf['MAX_ITEMS_SAVE'] = int(kwargs['max_items_save'])
            except ValueError:
                raise CloseSpider("You have to provide an integer value as max_items_save parameter!")
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "max_items_save " + str(self.conf['MAX_ITEMS_SAVE'])
        else:
            self.conf['MAX_ITEMS_SAVE'] = self.scraper.max_items_save
            
        super(DjangoSpider, self)._set_config(log_msg, **kwargs)


    def _check_scraper_config(self):
        try:
            self.scraper.get_base_elem() 
        except ScraperElem.DoesNotExist:
            raise CloseSpider('Please define a base scraper elem in your database!')
        try:
            self.scraper.get_detail_page_url_elem()
        except ScraperElem.DoesNotExist:
            raise CloseSpider('Please define a detail page url scraper elem in your database!')
        if(len(self.scraper.get_base_elems()) > 1):
            raise CloseSpider('A scraper can\'t have more than one base scraper elem!')
        if(len(self.scraper.get_detail_page_url_elems()) > 1):
            raise CloseSpider('A scraper can\'t have more than one detail page url scraper elem!')


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
            context_str = context_str.strip(', ')
            context = ast.literal_eval("{" + context_str + "}")
            context['spider'] = self
            self.loader.context = context
        except SyntaxError:
            self.log("Wrong context definition format: " + context_str, log.ERROR)


    def _get_processors(self, procs_str):
        procs = [TakeFirst(), processors.string_strip,]
        if not procs_str:
            return procs
        procs_tmp = list(procs_str.split(','))
        for p in procs_tmp:
            p = p.strip()
            if hasattr(processors, p):
                procs.append(getattr(processors, p))
            else:
                self.log("Processor '%s' is not defined!" % p, log.ERROR)
        procs = tuple(procs)
        return procs


    def _scrape_item_attr(self, scraper_elem):
        if(self.from_detail_page == scraper_elem.from_detail_page):
            procs = self._get_processors(scraper_elem.processors)
            self._set_loader_context(scraper_elem.proc_ctxt)
            
            static_ctxt = self.loader.context.get('static', '')
            if processors.static in procs and static_ctxt:
                self.loader.add_value(scraper_elem.scraped_obj_attr.name, static_ctxt)
            elif(scraper_elem.reg_exp):
                self.loader.add_xpath(scraper_elem.scraped_obj_attr.name, scraper_elem.x_path, *procs,  re=scraper_elem.reg_exp)
            else:
                self.loader.add_xpath(scraper_elem.scraped_obj_attr.name, scraper_elem.x_path, *procs)
            msg  = '{0: <20}'.format(scraper_elem.scraped_obj_attr.name)
            c_values = self.loader.get_collected_values(scraper_elem.scraped_obj_attr.name)
            if len(c_values) > 0:
                msg += "'" + c_values[0] + "'"
            else:
                msg += u'None'
            self.log(msg, log.DEBUG)


    def _set_loader(self, response, xs, item):
        if not xs:
            self.from_detail_page = True
            item = response.request.meta['item']
            self.loader = XPathItemLoader(item=item, response=response)
            self.loader.default_output_processor = TakeFirst()
        else:
            self.from_detail_page = False
            self.loader = XPathItemLoader(item=item, selector=xs)
            self.loader.default_output_processor = TakeFirst()


    def parse_item(self, response, xs=None):
        self._set_loader(response, xs, self.scraped_obj_item_class())
        if not self.from_detail_page:
            self.items_read_count += 1
            
        elems = self.scraper.get_scrape_elems()
        
        for elem in elems:
            self._scrape_item_attr(elem)
        # Dealing with Django Char- and TextFields defining blank field as null
        item = self.loader.load_item()
        for key, value in item.items():
            if value == None and \
               self.scraped_obj_class()._meta.get_field(key).blank and \
               not self.scraped_obj_class()._meta.get_field(key).null:
                item[key] = ''
        
        return item


    def parse(self, response):
        if self.scraper.content_type == 'H':
            xs = HtmlXPathSelector(response)
        else:
            xs = XmlXPathSelector(response)
        base_elem = self.scraper.get_base_elem()
        url_elem = self.scraper.get_detail_page_url_elem()
        base_objects = xs.select(base_elem.x_path)
        if(len(base_objects) == 0):
            self.log("No base objects found!", log.ERROR)
        
        if(self.conf['MAX_ITEMS_READ']):
            items_left = min(len(base_objects), self.conf['MAX_ITEMS_READ'] - self.items_read_count)
            base_objects = base_objects[0:items_left]
        
        for obj in base_objects:
            item_num = self.items_read_count + 1
            self.log("Starting to crawl item %s." % str(item_num), log.INFO)
            item = self.parse_item(response, obj)
            #print item
            url_name = url_elem.scraped_obj_attr.name
            if(item and url_name in item):
                url = item[url_name]
                cnt = self.scraped_obj_class.objects.filter(url=item[url_name]).count()
                cnt1 = self.scraper.get_standard_update_elems_from_detail_page().count()
                cnt2 = self.scraper.get_from_detail_page_scrape_elems().count()
                # Mark item as DOUBLE item
                if cnt > 0:
                    item[url_name] = 'DOUBLE' + item[url_name]
                # (DOUBLE item with no standard update elements to be scraped from detail page) or 
                # generally no attributes scraped from detail page
                if (cnt > 0 and cnt1 == 0) or cnt2 == 0:
                    yield item
                else:
                    yield Request(url, callback=self.parse_item, meta={'item':item})
            else:
                self.log("Detail page url elem could not be read!", log.ERROR)
    
