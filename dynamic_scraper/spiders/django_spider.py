# -*- coding: utf-8 -*-
#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from builtins import str
from builtins import map
from builtins import range
import ast, datetime, importlib, json, logging, scrapy

from jsonpath_rw import jsonpath, parse
from jsonpath_rw.lexer import JsonPathLexerError

from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, TakeFirst
from scrapy.exceptions import CloseSpider

from django.db.models.signals import post_save
from django.utils.encoding import smart_text

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.loader import JsonItemLoader
from dynamic_scraper.utils.scheduler import Scheduler
from dynamic_scraper.utils import processors



class DjangoSpider(DjangoBaseSpider):

    mp_form_data = None
    dp_form_data = {}
    tmp_non_db_results = {}
    non_db_results = {}
    
    current_output_num_mp_response_bodies = 0
    current_output_num_dp_response_bodies = 0

    def __init__(self, *args, **kwargs):
        self.mandatory_vars.append('scraped_obj_class')
        self.mandatory_vars.append('scraped_obj_item_class')
        
        super(DjangoSpider, self).__init__(self, *args, **kwargs)
    
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        
        spider._set_config(**kwargs)
        spider._set_request_kwargs()
        
        for cp_path in spider.conf['CUSTOM_PROCESSORS']:
            try:
                custom_processors = importlib.import_module(cp_path)
            except ImportError:
                msg = "Custom processors from {path} could not be imported, processors won't be applied".format(
                    path=cp_path,
                )
                spider.log(msg, logging.WARNING)
        
        post_save.connect(spider._post_save_tasks, sender=spider.scraped_obj_class)
        
        spider._set_start_urls(spider.scrape_url)
        spider.scheduler = Scheduler(spider.scraper.scraped_obj_class.scraper_scheduler_conf)
        spider.from_page = 'MP'
        spider.loader = None
        spider.dummy_loader = None
        spider.items_read_count = 0
        spider.items_save_count = 0
        
        msg = 'Spider for {roc} "{ro}" ({pk}) initialized.'.format(
            roc=spider.ref_object.__class__.__name__,
            ro=str(spider.ref_object),
            pk=str(spider.ref_object.pk),
        )
        spider.log(msg, logging.INFO)        
        
        return spider
    

    def output_usage_help(self):
        out = (
            '',
            'DDS Usage',
            '=========',
            '  scrapy crawl [scrapy_options] SPIDERNAME -a id=REF_OBJECT_ID [dds_options]',
            '',
            'Options',
            '-------',
            '-a do_action=(yes|no)                   Save output to DB, default: no (Test Mode)',
            '-L LOG_LEVEL (scrapy option)            Setting the log level for both Scrapy and DDS',
            '-a run_type=(TASK|SHELL)                Simulate task based scraper run, default: SHELL',
            '-a max_items_read=[Int]                 Limit number of items to read',
            '-a max_items_save=[Int]                 Limit number of items to save',
            '-a max_pages_read=[Int]                 Limit number of pages to read',
            '-a start_page=[PAGE]                    Start at page PAGE, e.g. 5, F',
            '-a end_page=[PAGE]                      End scraping at page PAGE, e.g. 10, M',
            '-a output_num_mp_response_bodies=[Int]  Output response body content of MP for debugging',
            '-a output_num_dp_response_bodies=[Int]  Output response body content of DP for debugging',
            '',
        )
        for out_str in out:
            self.dds_logger.info(out_str)
    

    def _set_request_kwargs(self):
        super(DjangoSpider, self)._set_request_kwargs()
        for rpt in self.scraper.requestpagetype_set.all():
            if rpt.form_data != '':
                try:
                    form_data = json.loads(rpt.form_data)
                except ValueError:
                    msg = "Incorrect form_data attribute ({pt}): not a valid JSON dict!".format(pt=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                if not isinstance(form_data, dict):
                    msg = "Incorrect form_data attribute ({pt}): not a valid JSON dict!".format(pt=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                if rpt.page_type == 'MP':
                    self.mp_form_data = form_data
                else:
                    self.dp_form_data[rpt.page_type] = form_data


    def _set_config(self, **kwargs):
        log_msg = ""
        #max_items_read 
        if 'max_items_read' in kwargs:
            try:
                self.conf['MAX_ITEMS_READ'] = int(kwargs['max_items_read'])
            except ValueError:
                msg = "You have to provide an integer value as max_items_read parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
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
                msg = "You have to provide an integer value as max_items_save parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "max_items_save " + str(self.conf['MAX_ITEMS_SAVE'])
        else:
            self.conf['MAX_ITEMS_SAVE'] = self.scraper.max_items_save
        #max_pages_read 
        if 'max_pages_read' in kwargs:
            try:
                self.conf['MAX_PAGES_READ'] = int(kwargs['max_pages_read'])
            except ValueError:
                msg = "You have to provide an integer value as max_pages_read parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "max_pages_read " + str(self.conf['MAX_PAGES_READ'])
        else:
            self.conf['MAX_PAGES_READ'] = None
        #start_page
        if 'start_page' in kwargs:
            self.conf['START_PAGE'] = kwargs['start_page']
        else:
            self.conf['START_PAGE'] = None
        #end_page
        if 'end_page' in kwargs:
            self.conf['END_PAGE'] = kwargs['end_page']
        else:
            self.conf['END_PAGE'] = None
        #output_num_mp_response_bodies
        if 'output_num_mp_response_bodies' in kwargs:
            try:
                self.conf['OUTPUT_NUM_MP_RESPONSE_BODIES'] = int(kwargs['output_num_mp_response_bodies'])
            except ValueError:
                msg = "You have to provide an integer value as output_num_mp_response_bodies parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "output_num_mp_response_bodies " + str(self.conf['OUTPUT_NUM_MP_RESPONSE_BODIES'])
        else:
            self.conf['OUTPUT_NUM_MP_RESPONSE_BODIES'] = 0
        #output_num_dp_response_bodies
        if 'output_num_dp_response_bodies' in kwargs:
            try:
                self.conf['OUTPUT_NUM_DP_RESPONSE_BODIES'] = int(kwargs['output_num_dp_response_bodies'])
            except ValueError:
                msg = "You have to provide an integer value as output_num_dp_response_bodies parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "output_num_dp_response_bodies " + str(self.conf['OUTPUT_NUM_DP_RESPONSE_BODIES'])
        else:
            self.conf['OUTPUT_NUM_DP_RESPONSE_BODIES'] = 0
            
        super(DjangoSpider, self)._set_config(log_msg, **kwargs)


    def limit_page_nums(self, pages):
        if self.conf['START_PAGE']:
            index = 0
            exists = False
            for page in pages:
                if str(page) == self.conf['START_PAGE']:
                    pages = pages[index:]
                    exists = True
                    break
                index += 1
            if not exists:
                msg = "The provided start page doesn't exist in the range of page values!"
                self.dds_logger.error(msg)
                raise CloseSpider()
        
        if self.conf['END_PAGE']:
            index = 0
            exists = False
            for page in pages:
                if str(page) == self.conf['END_PAGE']:
                    pages = pages[:index+1]
                    exists = True
                    break
                index += 1
            if not exists:
                msg = "The provided end page doesn't exist in the range of page values!"
                self.dds_logger.error(msg)
                raise CloseSpider()
        
        return pages
    
    
    def _set_start_urls(self, scrape_url):
        self.start_urls = []
        
        if self.scraper.pagination_type != 'N':
            if not self.scraper.pagination_page_replace:
                msg = 'Please provide a pagination_page_replace context corresponding to pagination_type!'
                self.dds_logger.error(msg)
                raise CloseSpider()
        
        if self.scraper.pagination_type == 'R':
            try:
                pages = self.scraper.pagination_page_replace
                pages = pages.split(',')
                if len(pages) > 3:
                    raise Exception
                pages = list(range(*list(map(int, pages))))
            except Exception:
                msg = 'Pagination_page_replace for pagination_type "RANGE_FUNCT" ' +\
                      'has to be provided as python range function arguments ' +\
                      '[start], stop[, step] (e.g. "1, 50, 10", no brackets)!'
                self.dds_logger.error(msg)
                raise CloseSpider()
            pages = self.limit_page_nums(pages)
        
        if self.scraper.pagination_type == 'F':
            try:
                pages = self.scraper.pagination_page_replace
                pages = pages.strip(', ')
                pages = ast.literal_eval("[" + pages + ",]")
            except:
                msg = 'Wrong pagination_page_replace format for pagination_type "FREE_LIST", ' +\
                      "Syntax: 'Replace string 1', 'Another replace string 2', 'A number 3', ..."
                self.dds_logger.error(msg)
                raise CloseSpider()
            pages = self.limit_page_nums(pages)
        
        if self.scraper.pagination_type != 'N':
            append_str = self.scraper.pagination_append_str
            if scrape_url[-1:] == '/' and append_str[0:1] == '/':
                append_str = append_str[1:]

            self.pages = pages
            if self.conf['MAX_PAGES_READ']:
                self.pages = self.pages[0:self.conf['MAX_PAGES_READ']]
            for page in self.pages:
                url = scrape_url + append_str.format(page=page)
                self.start_urls.append(url)
            if not self.scraper.pagination_on_start and not self.conf['START_PAGE']:
                self.start_urls.insert(0, scrape_url)
                self.pages.insert(0, "")
        
        if self.scraper.pagination_type == 'N':
            self.start_urls.append(scrape_url)
            self.pages = ["",]
        num = len(self.start_urls)
        if (num == 1):
            url_str = 'URL'
        else:
            url_str = 'URLs'
        self.log("Scraper set to run on {num} start {url_str}.".format(
            num=num, url_str=url_str), logging.INFO)


    def start_requests(self):
        index = 0
        for url in self.start_urls:
            self._set_meta_splash_args()
            kwargs = self.mp_request_kwargs.copy()
            if self.mp_form_data:
                form_data = self.mp_form_data.copy()
            else:
                form_data = None
            if 'headers' in kwargs:
                kwargs['headers'] = json.loads(json.dumps(kwargs['headers']).replace('{page}', str(self.pages[index])))
            if 'body' in kwargs:
                kwargs['body'] = kwargs['body'].replace('{page}', str(self.pages[index]))
            if 'cookies' in kwargs:
                kwargs['cookies'] = json.loads(json.dumps(kwargs['cookies']).replace('{page}', str(self.pages[index])))
            if form_data:
                form_data = json.loads(json.dumps(form_data).replace('{page}', str(self.pages[index])))
            if 'meta' not in kwargs:
                    kwargs['meta'] = {}
            kwargs['meta']['page'] = index + 1
            rpt = self.scraper.get_main_page_rpt()
            self.dds_logger.info('')
            self.dds_logger.info(self.bcolors['BOLD'] + '======================================================================================' + self.bcolors['ENDC'])
            self.struct_log("{es}{es2}Scraping data from page {page}.{ec}{ec}".format(
                page=index+1, es=self.bcolors['BOLD'], es2=self.bcolors['HEADER'], ec=self.bcolors['ENDC']))
            self.struct_log("URL     : {url}".format(url=url))
            self._log_request_info(rpt, kwargs)
            self.dds_logger.info(self.bcolors['BOLD'] + '======================================================================================' + self.bcolors['ENDC'])
            index += 1
            if rpt.request_type == 'R':
                yield Request(url, callback=self.parse, method=rpt.method, dont_filter=rpt.dont_filter, **kwargs)
            else:
                yield FormRequest(url, callback=self.parse, method=rpt.method, formdata=form_data, dont_filter=rpt.dont_filter, **kwargs)


    def _check_for_double_item(self, item):
        idf_elems = self.scraper.get_id_field_elems()
        num_item_idfs = 0
        for idf_elem in idf_elems:
            idf_name = idf_elem.scraped_obj_attr.name
            if idf_name in item:
                num_item_idfs += 1

        cnt_double = 0
        if len(idf_elems) > 0 and num_item_idfs == len(idf_elems):
            qs = self.scraped_obj_class.objects
            for idf_elem in idf_elems:
                idf_name = idf_elem.scraped_obj_attr.name
                qs = qs.filter(**{idf_name:item[idf_name]})
            cnt_double = qs.count()

        # Mark item as DOUBLE item
        if cnt_double > 0:
            item._is_double = True
            return item, True
        else:
            item._is_double = False
            return item, False


    def _get_processors(self, scraper_elem):
        procs_str = scraper_elem.processors
        attr_type = scraper_elem.scraped_obj_attr.attr_type
        if scraper_elem.use_default_procs:
            procs = [TakeFirst(), processors.string_strip,]
        else:
            procs = []
        if not procs_str:
            return procs
        procs_tmp = list(procs_str.split(','))
        for p in procs_tmp:
            p = p.strip()
            added = False
            if hasattr(processors, p):
                procs.append(getattr(processors, p))
                added = True
            for cp_path in self.conf['CUSTOM_PROCESSORS']:
                try:
                    custom_processors = importlib.import_module(cp_path)
                    if hasattr(custom_processors, p):
                        procs.append(getattr(custom_processors, p))
                        added = True
                except ImportError:
                    pass
            if not added:
                self.log("Processor '{p}' is not defined!".format(p=p), logging.ERROR)
        procs = tuple(procs)
        return procs


    def _set_loader_context(self, context_str):
        try:
            context_str = context_str.strip(', ')
            context = ast.literal_eval("{" + context_str + "}")
            context['spider'] = self
            self.loader.context = context
            self.dummy_loader.context = context
        except SyntaxError:
            self.log("Wrong context definition format: " + context_str, logging.ERROR)
    

    def _scrape_item_attr(self, scraper_elem, response, from_page, item_num):
        if(from_page == scraper_elem.request_page_type):
            procs = self._get_processors(scraper_elem)
            self._set_loader_context(scraper_elem.proc_ctxt)
            
            if not scraper_elem.scraped_obj_attr.save_to_db:
                name = 'tmp_field'
                loader = self.dummy_loader
            else:
                name = scraper_elem.scraped_obj_attr.name
                loader = self.loader

            static_ctxt = loader.context.get('static', '')
            
            self.log("Applying the following processors: {p_list}".format(
                p_list=str([p.__name__ if hasattr(p, '__name__') else type(p).__name__ for p in procs])), 
                logging.DEBUG)
            
            if processors.static in procs and static_ctxt:
                loader.add_value(name, static_ctxt)
            elif(scraper_elem.reg_exp):
                loader.add_xpath(name, scraper_elem.x_path, *procs,  re=scraper_elem.reg_exp)
            else:
                loader.add_xpath(name, scraper_elem.x_path, *procs)
            if not scraper_elem.scraped_obj_attr.save_to_db:
                item = loader.load_item()
                if name in item:
                    self.tmp_non_db_results[item_num][scraper_elem.scraped_obj_attr.name] = item[name]
            rpt = self.scraper.requestpagetype_set.filter(page_type=from_page)[0]
            rpt_str = rpt.get_content_type_display()
            if rpt.render_javascript:
                rpt_str += '-JS'
            rpt_str += '|' + rpt.method
            page_str = str(response.request.meta['page']) + '-'
            msg  = '{page_type: <4} {rpt_str: <13} {cs}{name: <20}{ce} {page}{num} '.format(page=page_str, num=str(item_num), name=name, rpt_str=rpt_str, page_type=from_page, cs=self.bcolors["BOLD"], ce=self.bcolors["ENDC"])
            c_values = loader.get_collected_values(name)
            if len(c_values) > 0:
                val_str = c_values[0]
                if self.conf['CONSOLE_LOG_LEVEL'] != 'DEBUG':
                    val_str = (val_str[:400] + '..') if len(val_str) > 400 else val_str
                msg += smart_text(val_str) + "'"
            else:
                msg += 'None'
            self.log(msg, logging.INFO)


    def _set_loader(self, response, from_page, xs, item):
        self.from_page = from_page
        rpt = self.scraper.get_rpt(from_page)
        if not self.from_page == 'MP':
            item = response.request.meta['item']
            if rpt.content_type == 'J':
                json_resp = json.loads(response.body_as_unicode())
                self.loader = JsonItemLoader(item=item, selector=json_resp)
            else:
                self.loader = ItemLoader(item=item, response=response)
        else:
            if rpt.content_type == 'J':
                self.loader = JsonItemLoader(item=item, selector=xs)
            else:
                self.loader = ItemLoader(item=item, selector=xs)
        self.loader.default_output_processor = TakeFirst()
        self.loader.log = self.log


    def _set_dummy_loader(self, response, from_page, xs, item):
        self.from_page = from_page
        rpt = self.scraper.get_rpt(from_page)
        if not self.from_page == 'MP':
            item = response.request.meta['item']
            if rpt.content_type == 'J':
                json_resp = json.loads(response.body_as_unicode())
                self.dummy_loader = JsonItemLoader(item=DummyItem(), selector=json_resp)
            else:
                self.dummy_loader = ItemLoader(item=DummyItem(), response=response)
        else:
            if rpt.content_type == 'J':
                self.dummy_loader = JsonItemLoader(item=DummyItem(), selector=xs)
            else:
                self.dummy_loader = ItemLoader(item=DummyItem(), selector=xs)
        self.dummy_loader.default_output_processor = TakeFirst()
        self.dummy_loader.log = self.log
    

    def parse_item(self, response, xs=None, from_page=None, item_num=None):
        #logging.info(str(response.request.meta))
        #logging.info(response.body_as_unicode())
        if not from_page:
            from_page = response.request.meta['from_page']
            item_num = response.request.meta['item_num']
        self._set_loader(response, from_page, xs, self.scraped_obj_item_class())
        self._set_dummy_loader(response, from_page, xs, self.scraped_obj_item_class())
        if from_page == 'MP':
            self.items_read_count += 1
        else:
            if self.current_output_num_dp_response_bodies < self.conf['OUTPUT_NUM_DP_RESPONSE_BODIES']:
                self.current_output_num_dp_response_bodies += 1
                self.log("Response body ({url})\n\n***** RP_DP_{num}_START *****\n{resp_body}\n***** RP_DP_{num}_END *****\n\n".format(
                    url=response.url,
                    resp_body=response.body,
                    num=self.current_output_num_dp_response_bodies), logging.INFO)
            
        elems = self.scraper.get_scrape_elems()
        
        for elem in elems:
            if not elem.scraped_obj_attr.save_to_db:
                self._set_dummy_loader(response, from_page, xs, self.scraped_obj_item_class())
            self._scrape_item_attr(elem, response, from_page, item_num)
        # Dealing with Django Char- and TextFields defining blank field as null
        item = self.loader.load_item()
        
        for key, value in list(item.items()):
            if value == None and \
               self.scraped_obj_class()._meta.get_field(key).blank and \
               not self.scraped_obj_class()._meta.get_field(key).null:
                item[key] = ''
        if from_page != 'MP':
            item, is_double = self._check_for_double_item(item)
            if response.request.meta['last']:
                self.non_db_results[id(item)] = self.tmp_non_db_results[item_num].copy()
                return item
        else:
            return item
    
    def _replace_placeholders(self, text_str, item, item_num):
        applied = []
        if type(text_str).__name__ != 'str' and type(text_str).__name__ != 'unicode':
            return text_str, applied
        standard_elems = self.scraper.get_standard_elems()
        for scraper_elem in standard_elems:
            if scraper_elem.request_page_type == 'MP':
                name = scraper_elem.scraped_obj_attr.name
                placeholder = '{' + name + '}'
                if not scraper_elem.scraped_obj_attr.save_to_db:
                    if name in self.tmp_non_db_results[item_num] and \
                       self.tmp_non_db_results[item_num][name] != None and \
                       placeholder in text_str:
                        text_str = text_str.replace(placeholder, self.tmp_non_db_results[item_num][name])
                        applied.append(placeholder)
                else:
                    if name in item and \
                       item[name] != None and \
                       placeholder in text_str:
                        text_str = text_str.replace(placeholder, item[name])
                        applied.append(placeholder)
        return text_str, applied


    def parse(self, response):
        xs = Selector(response)
        base_elem = self.scraper.get_base_elem()
        
        if self.current_output_num_mp_response_bodies < self.conf['OUTPUT_NUM_MP_RESPONSE_BODIES']:
            self.current_output_num_mp_response_bodies += 1
            self.log("Response body ({url})\n\n***** RP_MP_{num}_START *****\n{resp_body}\n***** RP_MP_{num}_END *****\n\n".format(
                url=response.url,
                resp_body=response.body,
                num=self.current_output_num_mp_response_bodies), logging.INFO)
        
        if self.scraper.get_main_page_rpt().content_type == 'J':
            json_resp = json.loads(response.body_as_unicode())
            try:
                jsonpath_expr = parse(base_elem.x_path)
            except JsonPathLexerError:
                msg = "JsonPath for base elem could not be processed!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            base_objects = [match.value for match in jsonpath_expr.find(json_resp)]
            if len(base_objects) > 0:
                base_objects = base_objects[0]
        else:
            base_objects = response.xpath(base_elem.x_path)

        if(len(base_objects) == 0):
            self.log("{cs}No base objects found.{ce}".format(
                cs=self.bcolors["INFO"], ce=self.bcolors["ENDC"]), logging.ERROR)
        
        if(self.conf['MAX_ITEMS_READ']):
            items_left = min(len(base_objects), self.conf['MAX_ITEMS_READ'] - self.items_read_count)
            base_objects = base_objects[0:items_left]
        

        for obj in base_objects:
            item_num = self.items_read_count + 1
            self.tmp_non_db_results[item_num] = {}
            self.dds_logger.info("")
            self.dds_logger.info(self.bcolors['BOLD'] + '--------------------------------------------------------------------------------------' + self.bcolors['ENDC'])
            self.struct_log("{cs}Starting to crawl item {i} from page {p}.{ce}".format(
                i=str(item_num), p=str(response.request.meta['page']), cs=self.bcolors["HEADER"], ce=self.bcolors["ENDC"]))
            self.dds_logger.info(self.bcolors['BOLD'] + '--------------------------------------------------------------------------------------' + self.bcolors['ENDC'])
            item = self.parse_item(response, obj, 'MP', item_num)
            item._dds_item_page = response.request.meta['page']
            item._dds_item_id = item_num
            
            if item:
                only_main_page_idfs = True
                idf_elems = self.scraper.get_id_field_elems()
                for idf_elem in idf_elems:
                    if idf_elem.request_page_type != 'MP':
                        only_main_page_idfs = False

                is_double = False
                if only_main_page_idfs:
                    item, is_double = self._check_for_double_item(item)
                
                # Don't go on reading detail pages when...
                # No detail page URLs defined or
                # DOUBLE item with only main page IDFs and no standard update elements to be scraped from detail pages or 
                # generally no attributes scraped from detail pages
                cnt_sue_detail = self.scraper.get_standard_update_elems_from_detail_pages().count()
                cnt_detail_scrape = self.scraper.get_from_detail_pages_scrape_elems().count()

                if self.scraper.get_detail_page_url_elems().count() == 0 or \
                    (is_double and cnt_sue_detail == 0) or cnt_detail_scrape == 0:
                    self.non_db_results[id(item)] = self.tmp_non_db_results[item_num].copy()
                    yield item
                else:
                    #self.run_detail_page_request()
                    url_elems = self.scraper.get_detail_page_url_elems()
                    for url_elem in url_elems:
                        if not url_elem.scraped_obj_attr.save_to_db:
                            url_before = self.tmp_non_db_results[item_num][url_elem.scraped_obj_attr.name]
                            url, applied = self._replace_placeholders(url_before, item, item_num)
                            self.tmp_non_db_results[item_num][url_elem.scraped_obj_attr.name] = url
                        else:
                            url_before = item[url_elem.scraped_obj_attr.name]
                            url, applied = self._replace_placeholders(url_before, item, item_num)
                            item[url_elem.scraped_obj_attr.name] = url
                        if len(applied) > 0:
                            msg = "Detail page URL placeholder(s) applied (item {p}-{n}): {a}".format(
                                a=str(applied), p=item._dds_item_page, n=item._dds_item_id)
                            self.log(msg, logging.DEBUG)
                            self.log("URL before: " + url_before, logging.DEBUG)
                            self.log("URL after : " + url, logging.DEBUG)
                        rpt = self.scraper.get_rpt_for_scraped_obj_attr(url_elem.scraped_obj_attr)
                        kwargs = self.dp_request_kwargs[rpt.page_type].copy()
                        
                        if 'meta' not in kwargs:
                            kwargs['meta'] = {}
                        kwargs['meta']['item'] = item
                        kwargs['meta']['from_page'] = rpt.page_type
                        kwargs['meta']['item_num'] = item_num
                        kwargs['meta']['page'] = response.request.meta['page']
                        
                        if 'headers' in kwargs:
                            for key, value in list(kwargs['headers'].items()):
                                new_value, applied = self._replace_placeholders(value, item, item_num)
                                kwargs['headers'][key] = new_value
                                if len(applied) > 0:
                                    msg = "Request info placeholder(s) applied (item {p}-{n}): {a}".format(
                                        a=str(applied), p=item._dds_item_page, n=item._dds_item_id)
                                    self.log(msg, logging.DEBUG)
                                    self.log("HEADERS [" + str(key) + "] before: " + str(value), logging.DEBUG)
                                    self.log("HEADERS [" + str(key) + "] after : " + str(new_value), logging.DEBUG)
                        if 'body' in kwargs:
                            body_before = kwargs['body']
                            kwargs['body'], applied = self._replace_placeholders(kwargs['body'], item, item_num)
                            if len(applied) > 0:
                                msg = "Request info placeholder(s) applied (item {p}-{n}): {a}".format(
                                    a=str(applied), p=item._dds_item_page, n=item._dds_item_id)
                                self.log(msg, logging.DEBUG)
                                self.log("BODY before: " + body_before, logging.DEBUG)
                                self.log("BODY after : " + kwargs['body'], logging.DEBUG)
                        if 'cookies' in kwargs:
                            for key, value in list(kwargs['cookies'].items()):
                                new_value, applied = self._replace_placeholders(value, item, item_num)
                                kwargs['cookies'][key] = new_value
                                if len(applied) > 0:
                                    msg = "Request info placeholder(s) applied (item {p}-{n}): {a}".format(
                                        a=str(applied), p=item._dds_item_page, n=item._dds_item_id)
                                    self.log(msg, logging.DEBUG)
                                    self.log("COOKIE [" + str(key) + "] before: " + str(value), logging.DEBUG)
                                    self.log("COOKIE [" + str(key) + "] after : " + str(new_value), logging.DEBUG)
                        if rpt.request_type == 'F' and rpt.page_type in self.dp_form_data:
                            for key, value in list(self.dp_form_data[rpt.page_type].items()):
                                new_value, applied = self._replace_placeholders(value, item, item_num)
                                self.dp_form_data[rpt.page_type][key] = new_value
                                if len(applied) > 0:
                                    msg = "Request info placeholder(s) applied (item {p}-{n}): {a}".format(
                                        a=str(applied), p=item._dds_item_page, n=item._dds_item_id)
                                    self.log(msg, logging.DEBUG)
                                    self.log("FORM DATA [" + str(key) + "] before: " + str(value), logging.DEBUG)
                                    self.log("FORM DATA [" + str(key) + "] after : " + str(new_value), logging.DEBUG)
                        
                        if url_elem == url_elems[len(url_elems)-1]:
                            kwargs['meta']['last'] = True
                        else:
                            kwargs['meta']['last'] = False
                        self._set_meta_splash_args()
                        #logging.info(str(kwargs))
                        self.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logging.INFO)
                        msg = "{cs}Calling {dp} URL for item {p}-{n}...{ce}".format(
                            dp=rpt.page_type, p=str(response.request.meta['page']), n=str(item_num),
                            cs=self.bcolors["HEADER"], ce=self.bcolors["ENDC"])
                        self.log(msg, logging.INFO)
                        msg = "URL     : {url}".format(url=url)
                        self.log(msg, logging.INFO)
                        self._log_request_info(rpt, kwargs)
                        self.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logging.INFO)
                        
                        if rpt.request_type == 'R':
                            yield Request(url, callback=self.parse_item, method=rpt.method, dont_filter=rpt.dont_filter, **kwargs)
                        else:
                            yield FormRequest(url, callback=self.parse_item, method=rpt.method, formdata=self.dp_form_data[rpt.page_type], dont_filter=rpt.dont_filter, **kwargs)
            else:
                self.log("Item could not be read!", logging.ERROR)
    
    
    def _log_request_info(self, rpt, kwargs):
        level = logging.DEBUG
        extra_info = False
        if 'headers' in kwargs:
            self.log("HEADERS   : " + str(kwargs['headers']), level)
            extra_info = True
        if 'body' in kwargs:
            self.log("BODY      : " + str(kwargs['body']), level)
            extra_info = True
        if 'cookies' in kwargs:
            self.log("COOKIES   : " + str(kwargs['cookies']), level)
            extra_info = True
        if rpt.request_type == 'F':
            if rpt.page_type in self.dp_form_data:
                self.log("FORM DATA : " + str(self.dp_form_data[rpt.page_type]), level)
                extra_info = True
            if rpt.page_type == 'MP':
                self.log("FORM DATA : " + str(self.mp_form_data), level)
                extra_info = True
        
        if not extra_info:
            self.log("No additional request information sent.", level)
    
    
    def _post_save_tasks(self, sender, instance, created, **kwargs):
        if instance and created:
            self.scraper.last_scraper_save = datetime.datetime.now()
            self.scraper.save()
    

class DummyItem(scrapy.Item):
    tmp_field = scrapy.Field()
