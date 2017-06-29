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
            '-a do_action=(yes|no)                       Save output to DB, default: no (Test Mode or File Output)',
            '-L LOG_LEVEL (scrapy option)                Setting the log level for both Scrapy and DDS',
            '-a run_type|rt=(TASK|SHELL)                 Simulate task based scraper run, default: SHELL',
            '-a max_items_read|mir=[Int]                 Limit number of items to read',
            '-a max_items_save|mis=[Int]                 Limit number of items to save',
            '-a max_pages_read|mpr=[Int]                 Limit number of pages to read (static pagination)',
            '-a start_page|sp=[PAGE]                     Start at page PAGE, e.g. 5, F (static pagination)',
            '-a end_page|ep=[PAGE]                       End scraping at page PAGE, e.g. 10, M (static pagination)',
            '-a num_pages_follow|npf=[Int]               Number of pages to follow (dynamic pagination)',
            '-a output_num_mp_response_bodies|omp=[Int]  Output response body content of MP for debugging',
            '-a output_num_dp_response_bodies|odb=[Int]  Output response body content of DP for debugging',
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


    def _set_config(self, **kwargs):
        log_msg = ""
        #max_items_read|mir
        if 'mir' in kwargs:
            kwargs['max_items_read'] = kwargs['mir']
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
        #max_items_save|mis
        if 'mis' in kwargs:
            kwargs['max_items_save'] = kwargs['mis']
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
        #max_pages_read|mpr
        if 'mpr' in kwargs:
            kwargs['max_pages_read'] = kwargs['mpr'] 
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
        #start_page|sp
        if 'sp' in kwargs:
            kwargs['start_page'] = kwargs['sp']
        if 'start_page' in kwargs:
            self.conf['START_PAGE'] = kwargs['start_page']
        else:
            self.conf['START_PAGE'] = None
        #end_page|ep
        if 'ep' in kwargs:
            kwargs['end_page'] = kwargs['ep']
        if 'end_page' in kwargs:
            self.conf['END_PAGE'] = kwargs['end_page']
        else:
            self.conf['END_PAGE'] = None
        #num_pages_follow|npf
        if 'npf' in kwargs:
            kwargs['num_pages_follow'] = kwargs['npf']
        if 'num_pages_follow' in kwargs:
            try:
                self.conf['NUM_PAGES_FOLLOW'] = int(kwargs['num_pages_follow'])
            except ValueError:
                msg = "You have to provide an integer value as num_pages_follow parameter!"
                self.dds_logger.error(msg)
                raise CloseSpider()
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "num_pages_follow " + str(self.conf['NUM_PAGES_FOLLOW'])
        else:
            self.conf['NUM_PAGES_FOLLOW'] = self.scraper.num_pages_follow
        #output_num_mp_response_bodies|omp
        if 'omp' in kwargs:
            kwargs['output_num_mp_response_bodies'] = kwargs['omp']
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
        #output_num_dp_response_bodies|odp
        if 'odp' in kwargs:
            kwargs['output_num_dp_response_bodies'] = kwargs['odp']
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
        
        if self.scraper.pagination_type in ['R', 'F',]:
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
        
        if self.scraper.pagination_type in ['R', 'F',]:
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
        
        if self.scraper.pagination_type in ['N', 'O',]:
            self.start_urls.append(scrape_url)
            self.pages = ["",]
        num = len(self.start_urls)
        if (num == 1):
            url_str = 'URL'
        else:
            url_str = 'URLs'
        self.log("Scraper set to run on {num} start {url_str}.".format(
            num=num, url_str=url_str), logging.INFO)
    
    
    def _prepare_mp_req_data(self, kwargs_orig, form_data_orig, page, follow_page=''):
        kwargs = kwargs_orig.copy()
        if 'meta' not in kwargs:
                kwargs['meta'] = {}
        form_data = None
        if form_data_orig:
            form_data = json.loads(form_data_orig).copy()
        if 'headers' in kwargs:
            kwargs['headers'] = json.loads(json.dumps(kwargs['headers']).replace('{page}', str(page)))
            kwargs['headers'] = json.loads(json.dumps(kwargs['headers']).replace('{follow_page}', str(follow_page)))
        if 'body' in kwargs:
            kwargs['body'] = kwargs['body'].replace('{page}', str(page))
            kwargs['body'] = kwargs['body'].replace('{follow_page}', str(follow_page))
        if 'cookies' in kwargs:
            kwargs['cookies'] = json.loads(json.dumps(kwargs['cookies']).replace('{page}', str(page)))
            kwargs['cookies'] = json.loads(json.dumps(kwargs['cookies']).replace('{follow_page}', str(follow_page)))
        if form_data:
            form_data = json.loads(json.dumps(form_data).replace('{page}', str(page)))
            form_data = json.loads(json.dumps(form_data).replace('{follow_page}', str(follow_page)))
        return kwargs, form_data
    
    
    def _log_page_info(self, page_num, follow_page_num, url, rpt, form_data, kwargs):
        self.dds_logger.info('')
        self.dds_logger.info(self.bcolors['BOLD'] + '======================================================================================' + self.bcolors['ENDC'])
        self.struct_log("{es}{es2}Scraping data from page {p}({fp}).{ec}{ec}".format(
            p=page_num, fp=follow_page_num, es=self.bcolors['BOLD'], es2=self.bcolors['HEADER'], ec=self.bcolors['ENDC']))
        self.struct_log("URL     : {url}".format(url=url))
        self._log_request_info(rpt, form_data, kwargs)
        self.dds_logger.info(self.bcolors['BOLD'] + '======================================================================================' + self.bcolors['ENDC'])
    
    
    def start_requests(self):
        index = 0
        rpt = self.scraper.get_main_page_rpt()
        follow_page_num = 0
        
        for url in self.start_urls:
            self._set_meta_splash_args()
            page_num = index + 1
            kwargs, form_data = self._prepare_mp_req_data(self.mp_request_kwargs, self.scraper.get_main_page_rpt().form_data, self.pages[index])
            kwargs['meta']['page_num'] = page_num
            kwargs['meta']['follow_page_num'] = follow_page_num
            kwargs['meta']['rpt'] = rpt
            self._log_page_info(page_num, follow_page_num, url, rpt, form_data, kwargs)
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
        if(from_page == scraper_elem.request_page_type or 
            (from_page == 'FP' and scraper_elem.request_page_type == 'MP')):
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
            page_str = str(response.request.meta['page_num'])
            page_str += '(' + str(response.request.meta['follow_page_num']) + ')-'
            msg  = '{page_type: <4} {rpt_str: <13} {cs}{name: <20}{ce} {page}{num} '.format(page=page_str, num=str(item_num), name=name, rpt_str=rpt_str, page_type=from_page, cs=self.bcolors["BOLD"], ce=self.bcolors["ENDC"])
            c_values = loader.get_collected_values(name)
            if len(c_values) > 0:
                val_str = c_values[0]
                if self.conf['CONSOLE_LOG_LEVEL'] != 'DEBUG':
                    val_str = (val_str[:400] + '..') if len(val_str) > 400 else val_str
                msg += smart_text(val_str)
            else:
                msg += 'None'
            self.log(msg, logging.INFO)


    def _set_loader(self, response, from_page, xs, item):
        self.from_page = from_page
        rpt = self.scraper.get_rpt(from_page)
        if not (self.from_page == 'MP' or self.from_page == 'FP'):
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
        if not (self.from_page == 'MP' or self.from_page == 'FP'):
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
        if from_page == 'MP' or from_page == 'FP':
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
        if not (from_page == 'MP' or from_page == 'FP'):
            item, is_double = self._check_for_double_item(item)
            if response.request.meta['last']:
                self.non_db_results[id(item)] = self.tmp_non_db_results[item_num].copy()
                return item
        else:
            return item
    
    def _replace_placeholders(self, text_str, item, item_num, only_mp):
        applied = []
        if type(text_str).__name__ != 'str' and type(text_str).__name__ != 'unicode':
            return text_str, applied
        standard_elems = self.scraper.get_standard_elems()
        for scraper_elem in standard_elems:
            if not only_mp or scraper_elem.request_page_type == 'MP':
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


    def _do_req_info_replacements(self, item, item_num, page, json_dict, info_str):
        json_dict = json.loads(json.dumps(json_dict).replace('{page}', str(page)))
        for key, value in list(json_dict.items()):
            new_value, applied = self._replace_placeholders(value, item, item_num, True)
            json_dict[key] = new_value
            if len(applied) > 0:
                msg = "Request info placeholder(s) applied (item {id}): {a}".format(
                    a=str(applied), id=item._dds_id_str)
                self.log(msg, logging.DEBUG)
                self.log(info_str + " [" + str(key) + "] before: " + str(value), logging.DEBUG)
                self.log(info_str + " [" + str(key) + "] after : " + str(new_value), logging.DEBUG)
        return json_dict
    
    

    def parse(self, response):
        xs = Selector(response)
        base_objects = []
        base_elem = self.scraper.get_base_elem()
        rpt = response.request.meta['rpt']
        
        page_num = response.request.meta['page_num']
        page = self.pages[page_num - 1]
        follow_page_num = response.request.meta['follow_page_num']
        
        if rpt.page_type == 'MP':
            if self.current_output_num_mp_response_bodies < self.conf['OUTPUT_NUM_MP_RESPONSE_BODIES']:
                self.current_output_num_mp_response_bodies += 1
                self.log("Response body ({url})\n\n***** RP_MP_{num}_START *****\n{resp_body}\n***** RP_MP_{num}_END *****\n\n".format(
                    url=response.url,
                    resp_body=response.body,
                    num=self.current_output_num_mp_response_bodies), logging.INFO)
        
        if rpt.content_type == 'J':
            json_resp = None
            try:
                json_resp = json.loads(response.body_as_unicode())
            except ValueError:
                msg = "JSON response for MP could not be parsed!"
                self.log(msg, logging.ERROR)
            if json_resp:
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
            page_str = str(page_num) + '(' + str(follow_page_num) + ')'
            self.dds_logger.info("")
            self.dds_logger.info(self.bcolors['BOLD'] + '--------------------------------------------------------------------------------------' + self.bcolors['ENDC'])
            self.struct_log("{cs}Starting to crawl item {i} from page {p}.{ce}".format(
                i=str(item_num), p=page_str, cs=self.bcolors["HEADER"], ce=self.bcolors["ENDC"]))
            self.dds_logger.info(self.bcolors['BOLD'] + '--------------------------------------------------------------------------------------' + self.bcolors['ENDC'])
            item = self.parse_item(response, obj, rpt.page_type, item_num)
            item._dds_item_page = page_num
            item._dds_item_follow_page = follow_page_num
            item._dds_item_id = item_num
            item._dds_id_str = str(item._dds_item_page) + '(' + str(item._dds_item_follow_page) + ')-' + str(item._dds_item_id)
            
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
                            url, applied = self._replace_placeholders(url_before, item, item_num, True)
                            self.tmp_non_db_results[item_num][url_elem.scraped_obj_attr.name] = url
                        else:
                            url_before = item[url_elem.scraped_obj_attr.name]
                            url, applied = self._replace_placeholders(url_before, item, item_num, True)
                            item[url_elem.scraped_obj_attr.name] = url
                        if len(applied) > 0:
                            msg = "Detail page URL placeholder(s) applied (item {id}): {a}".format(
                                a=str(applied), id=item._dds_id_str)
                            self.log(msg, logging.DEBUG)
                            self.log("URL before: " + url_before, logging.DEBUG)
                            self.log("URL after : " + url, logging.DEBUG)
                        dp_rpt = self.scraper.get_rpt_for_scraped_obj_attr(url_elem.scraped_obj_attr)
                        kwargs = self.dp_request_kwargs[dp_rpt.page_type].copy()
                        
                        if 'meta' not in kwargs:
                            kwargs['meta'] = {}
                        kwargs['meta']['page_num'] = page_num
                        kwargs['meta']['follow_page_num'] = follow_page_num
                        kwargs['meta']['item'] = item
                        kwargs['meta']['from_page'] = dp_rpt.page_type
                        kwargs['meta']['item_num'] = item_num
                        
                        kwargs['meta']['rpt'] = dp_rpt
                        
                        if 'headers' in kwargs:
                            kwargs['headers'] = self._do_req_info_replacements(item, item_num, page, kwargs['headers'], "HEADERS")
                        if 'body' in kwargs:
                            body_before = kwargs['body']
                            kwargs['body'] = kwargs['body'].replace('{page}', str(page))
                            kwargs['body'], applied = self._replace_placeholders(kwargs['body'], item, item_num, True)
                            if len(applied) > 0:
                                msg = "Request info placeholder(s) applied (item {id}): {a}".format(
                                    a=str(applied), id=item._dds_id_str)
                                self.log(msg, logging.DEBUG)
                                self.log("BODY before: " + body_before, logging.DEBUG)
                                self.log("BODY after : " + kwargs['body'], logging.DEBUG)
                        if 'cookies' in kwargs:
                            kwargs['cookies'] = self._do_req_info_replacements(item, item_num, page, kwargs['cookies'], "COOKIES")
                        form_data = None
                        if dp_rpt.request_type == 'F' and dp_rpt.form_data:
                            form_data = json.loads(dp_rpt.form_data).copy()
                            form_data = self._do_req_info_replacements(item, item_num, page, form_data, "FORM DATA")
                        
                        if url_elem == url_elems[len(url_elems)-1]:
                            kwargs['meta']['last'] = True
                        else:
                            kwargs['meta']['last'] = False
                        self._set_meta_splash_args()
                        #logging.info(str(kwargs))
                        self.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logging.INFO)
                        msg = "{cs}Calling {dp} URL for item {id}...{ce}".format(
                            dp=dp_rpt.page_type, id=item._dds_id_str,
                            cs=self.bcolors["HEADER"], ce=self.bcolors["ENDC"])
                        self.log(msg, logging.INFO)
                        msg = "URL     : {url}".format(url=url)
                        self.log(msg, logging.INFO)
                        self._log_request_info(dp_rpt, form_data, kwargs)
                        self.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logging.INFO)
                        
                        if dp_rpt.request_type == 'R':
                            yield response.follow(url, callback=self.parse_item, method=dp_rpt.method, dont_filter=dp_rpt.dont_filter, **kwargs)
                        else:
                            yield FormRequest(url, callback=self.parse_item, method=dp_rpt.method, formdata=form_data, dont_filter=dp_rpt.dont_filter, **kwargs)
                for key, value in list(item.items()):
                    #Fixing some extremely weird Python 2 encoding failure, 2017-06-29
                    if type(value).__name__ == 'str':
                        try:
                            value = value.decode('utf-8')
                        except AttributeError:
                            pass
                    if value and (type(value).__name__ in ['str', 'unicode']) and '{page}' in value:
                        msg = "Applying page placeholder on {k}...".format(k=key)
                        self.log(msg, logging.DEBUG)
                        self.log("Value before: " + value, logging.DEBUG)
                        value = value.replace('{page}', str(page))
                        item[key] = value
                        self.log("Value after: " + value, logging.DEBUG)
            else:
                self.log("Item could not be read!", logging.ERROR)
                
        mir_reached = False
        if self.conf['MAX_ITEMS_READ'] and (self.conf['MAX_ITEMS_READ'] - self.items_read_count <= 0):
            mir_reached = True
        if self.scraper.follow_pages_url_xpath and not mir_reached:
            if not self.conf['NUM_PAGES_FOLLOW'] or follow_page_num < self.conf['NUM_PAGES_FOLLOW']:
                url = response.xpath(self.scraper.follow_pages_url_xpath).extract_first()
                if url is not None:
                    self._set_meta_splash_args()
                    follow_page = ''
                    if self.scraper.follow_pages_page_xpath:
                        follow_page = response.xpath(self.scraper.follow_pages_page_xpath).extract_first()
                    form_data_orig = None
                    if self.scraper.get_follow_page_rpts().count() > 0:
                        f_rpt = self.scraper.get_follow_page_rpts()[0]
                        form_data_orig = self.scraper.get_follow_page_rpts()[0].form_data
                    else:
                        f_rpt = self.scraper.get_main_page_rpt()
                        form_data_orig = self.scraper.get_main_page_rpt().form_data
                    kwargs, form_data = self._prepare_mp_req_data(self.fp_request_kwargs, form_data_orig, page, follow_page)
                    
                    follow_page_num += 1
                    kwargs['meta']['page_num'] = page_num
                    kwargs['meta']['follow_page_num'] = follow_page_num
                    kwargs['meta']['rpt'] = f_rpt
                    
                    self._log_page_info(page_num, follow_page_num, url, f_rpt, form_data, kwargs)
                    
                    if f_rpt.request_type == 'R':
                        yield response.follow(url, callback=self.parse, method=f_rpt.method, dont_filter=f_rpt.dont_filter, **kwargs)
                    else:
                        url = response.urljoin(url)
                        yield FormRequest(url, callback=self.parse, method=f_rpt.method, formdata=form_data, dont_filter=f_rpt.dont_filter, **kwargs)
    
    
    def _log_request_info(self, rpt, form_data, kwargs):
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
        if rpt.request_type == 'F' and form_data:
                self.log("FORM DATA : " + str(form_data), level)
                extra_info = True
        
        if not extra_info:
            self.log("No additional request information sent.", level)
    
    
    def _post_save_tasks(self, sender, instance, created, **kwargs):
        if instance and created:
            self.scraper.last_scraper_save = datetime.datetime.now()
            self.scraper.save()
    

class DummyItem(scrapy.Item):
    tmp_field = scrapy.Field()
