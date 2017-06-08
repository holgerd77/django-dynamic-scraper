#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from builtins import str
import datetime, json, logging, os, sys
from django.db import connection
from scrapy import signals
from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider
from pydispatch import dispatcher
from scrapy.exceptions import CloseSpider, UsageError

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from dynamic_scraper.models import Log, LogMarker


class NoParsingFilter(logging.Filter):
    def filter(self, record=True):
        return False
npf = NoParsingFilter()
logging.getLogger('twisted').addFilter(npf)


class DjangoBaseSpider(CrawlSpider):
    
    name = None
    action_successful = False
    mandatory_vars = ['ref_object', 'scraper', 'scrape_url',]
    allowed_domains = []
    start_urls = []
    conf = {
        "DO_ACTION": False,
        "RUN_TYPE": 'SHELL',
        "SPLASH_ARGS": {},
        "IMAGES_STORE_FORMAT": 'FLAT',
        "CUSTOM_PROCESSORS": [],
        "LOG_ENABLED": True,
        "LOG_LEVEL": 'ERROR',
        "LOG_LIMIT": 250,
        "CONSOLE_LOG_LEVEL": 'DEBUG',
    }
    
    bcolors = {
        "HEADER": '\033[95m',
        "OK": '\033[92m',
        "INFO": '\033[33m',
        "ERROR": '\033[91m',
        "ENDC": '\033[0m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m',
    }

    mp_request_kwargs = {}
    dp_request_kwargs = {}
    
    
    def __init__(self, *args, **kwargs):
        msg = "Django settings used: {s}".format(s=os.environ.get("DJANGO_SETTINGS_MODULE"))
        self.dds_logger = logging.getLogger('dds')
        self.dds_logger.info(msg)
        super(DjangoBaseSpider,  self).__init__(None, **kwargs)
        
        self._check_mandatory_vars()
        

    def _set_ref_object(self, ref_object_class, **kwargs):
        self.dds_logger = logging.getLogger('dds')
        
        if not 'id' in kwargs:
            msg = "{cs}You have to provide the ID of the reference {type} object.{ce}".format(
                type=ref_object_class.__name__, cs=self.bcolors["ERROR"], ce=self.bcolors["ENDC"])
            self.dds_logger.error(msg)
            self.output_usage_help()
            raise UsageError()
        try:
            self.ref_object = ref_object_class.objects.get(pk=kwargs['id'])
        except ObjectDoesNotExist:
            msg = "{cs}{type} object with ID {id} not found.{ce}".format(
                id=kwargs['id'], type=ref_object_class.__name__,
                cs=self.bcolors["ERROR"], ce=self.bcolors["ENDC"])
            self.dds_logger.error(msg)
            self.output_usage_help()
            raise UsageError()


    def _set_config(self, log_msg, **kwargs):
        #run_type
        if 'run_type' in kwargs:
            self.conf['RUN_TYPE'] = kwargs['run_type']
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "run_type " + self.conf['RUN_TYPE']
        #do_action
        if 'do_action' in kwargs:
            if kwargs['do_action'] == 'yes':
                self.conf['DO_ACTION'] = True
            else:
                self.conf['DO_ACTION'] = False
            if len(log_msg) > 0:
                log_msg += ", "
            log_msg += "do_action " + str(self.conf['DO_ACTION'])
        else:
            self.log("Running in Test Mode (do_action not set).", logging.INFO)
        
        if self.settings['DSCRAPER_SPLASH_ARGS']:
            self.conf['SPLASH_ARGS'] = self.settings['DSCRAPER_SPLASH_ARGS'] 
        if 'wait' not in self.conf['SPLASH_ARGS']:
            self.conf['SPLASH_ARGS']['wait'] = 0.5
        
        if self.settings['DSCRAPER_IMAGES_STORE_FORMAT']:
            self.conf['IMAGES_STORE_FORMAT'] = self.settings['DSCRAPER_IMAGES_STORE_FORMAT']
        if self.conf["IMAGES_STORE_FORMAT"] == 'FLAT':
            msg = "Use simplified FLAT images store format (save the original or one thumbnail image)"
            self.dds_logger.info(msg)
            if self.settings['DSCRAPER_IMAGES_THUMBS'] and len(self.settings['DSCRAPER_IMAGES_THUMBS']) > 0:
                msg =  "IMAGES_THUMBS setting found, saving images as thumbnail images "
                msg += "with size {size} (first entry)".format(
                    size=next(iter(self.settings['DSCRAPER_IMAGES_THUMBS'].keys())))
            else:
                msg = "IMAGES_THUMBS setting not found, saving images with original size"
            self.dds_logger.info(msg)
        elif self.conf["IMAGES_STORE_FORMAT"] == 'ALL':
            msg = "Use ALL images store format (Scrapy behaviour, save both original and thumbnail images)"
            self.dds_logger.info(msg)
        else:
            msg = "Use THUMBS images store format (save only the thumbnail images)"
            self.dds_logger.info(msg)
            
        if self.settings['DSCRAPER_CUSTOM_PROCESSORS']:
            self.conf['CUSTOM_PROCESSORS'] = self.settings['DSCRAPER_CUSTOM_PROCESSORS']
        
        if self.settings['DSCRAPER_LOG_ENABLED']:
            self.conf['LOG_ENABLED'] = self.settings['DSCRAPER_LOG_ENABLED']
        if self.settings['DSCRAPER_LOG_LEVEL']:
            self.conf['LOG_LEVEL'] = self.settings['DSCRAPER_LOG_LEVEL']
        if self.settings['LOG_LEVEL']:
            self.conf['CONSOLE_LOG_LEVEL'] = self.settings['LOG_LEVEL']
        
        if self.settings['DSCRAPER_LOG_LIMIT']:
            self.conf['LOG_LIMIT'] = self.settings['DSCRAPER_LOG_LIMIT']
        if log_msg == "":
            log_msg = "{}"
        self.log("Runtime config: " + log_msg, logging.INFO)
        
        if self.conf['CONSOLE_LOG_LEVEL'] == 'DEBUG':
            logging.getLogger('twisted').removeFilter(npf)
        if self.conf['CONSOLE_LOG_LEVEL'] != 'DEBUG':
            logging.getLogger('scrapy.middleware').addFilter(npf)
        
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)


    def _check_mandatory_vars(self):
        if self.conf['RUN_TYPE'] == 'TASK':
            if not getattr(self, 'scheduler_runtime', None):
                msg = "You have to provide a scheduler_runtime when running with run_type TASK."
                self.dds_logger.error(msg)
                raise CloseSpider(msg)
            msg = "SchedulerRuntime (" + str(self.scheduler_runtime) + ") found."
            self.log(msg, logging.INFO)
        
        for var in self.mandatory_vars:
            attr = getattr(self, var, None)
            if not attr:
                msg = "Missing attribute {a}.".format(a=var)
                self.dds_logger.error(msg)
                raise CloseSpider(msg)
            
        if self.scraper.status == 'P' or self.scraper.status == 'I':
            msg = 'Scraper status set to {s}!'.format(s=self.scraper.get_status_display())
            self.log(msg, logging.WARNING)
            raise CloseSpider(msg)


    def _set_request_kwargs(self):
        try:
            self.scraper.get_main_page_rpt()
        except ObjectDoesNotExist:
            msg = "Scraper must have exactly one main page request page type!"
            self.dds_logger.error(msg)
            raise CloseSpider()

        for rpt in self.scraper.requestpagetype_set.all():
            if rpt.page_type == 'MP':
                pt_dict = self.mp_request_kwargs
            else:
                self.dp_request_kwargs[rpt.page_type] = {}
                pt_dict = self.dp_request_kwargs[rpt.page_type]

            if rpt.headers != '':
                try:
                    headers = json.loads(rpt.headers)
                except ValueError:
                    msg = "Incorrect HTTP header attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                if not isinstance(headers, dict):
                    msg = "Incorrect HTTP header attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                pt_dict['headers'] = headers

            if rpt.body != '':
                pt_dict['body'] = rpt.body

            if rpt.cookies != '':
                try:
                    cookies = json.loads(rpt.cookies)
                except ValueError:
                    msg = "Incorrect cookies attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                if not isinstance(cookies, dict):
                    msg = "Incorrect cookies attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                pt_dict['cookies'] = cookies

            if rpt.meta != '':
                try:
                    meta = json.loads(rpt.meta)
                except ValueError:
                    msg = "Incorrect meta attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                if not isinstance(meta, dict):
                    msg = "Incorrect meta attribute ({a}): not a valid JSON dict!".format(a=rpt.page_type)
                    self.dds_logger.error(msg)
                    raise CloseSpider()
                pt_dict['meta'] = meta
    

    def _set_meta_splash_args(self):
        for rpt in self.scraper.requestpagetype_set.all():
            if rpt.page_type == 'MP':
                pt_dict = self.mp_request_kwargs
            else:
                pt_dict = self.dp_request_kwargs[rpt.page_type]
            if rpt.content_type == 'H' and rpt.render_javascript:
                if 'meta' not in pt_dict:
                    pt_dict['meta'] = {}
                pt_dict['meta']['splash'] = {
                    'endpoint': 'render.html',
                    'args': self.conf['SPLASH_ARGS'].copy()
                }
    
    
    def struct_log(self, msg):
        level = self.conf['CONSOLE_LOG_LEVEL']
        if level == 'INFO' or level == 'DEBUG':
            self.log(msg, logging.INFO)
        else:
            self.log(msg, logging.WARNING)
    

    def spider_closed(self):
        if self.conf['RUN_TYPE'] == 'TASK' and self.conf['DO_ACTION']:
            
            time_delta, factor, num_crawls = self.scheduler.calc_next_action_time(\
                    self.action_successful,\
                    self.scheduler_runtime.next_action_factor,\
                    self.scheduler_runtime.num_zero_actions)
            self.scheduler_runtime.next_action_time = datetime.datetime.now() + time_delta
            self.scheduler_runtime.next_action_factor = factor
            self.scheduler_runtime.num_zero_actions = num_crawls
            self.scheduler_runtime.save()
            msg  = "Scheduler runtime updated (Next action time: "
            msg += "{nat}, ".format(nat=str(self.scheduler_runtime.next_action_time.strftime("%Y-%m-%d %H:%m")))
            msg += "Next action factor: {naf}, ".format(naf=str(self.scheduler_runtime.next_action_factor))
            msg += "Zero actions: {za})".format(za=str(self.scheduler_runtime.num_zero_actions))
            self.log(msg, logging.INFO)
        
        self.log("Closing Django DB connection.", logging.INFO)
        connection.close()
    
    
    def log(self, message, level=logging.DEBUG):
        if self.conf['RUN_TYPE'] == 'TASK' and self.conf['DO_ACTION']:
            
            if self.conf['LOG_ENABLED'] and level >= getattr(logging, self.conf['LOG_LEVEL']):
                l = Log()
                l.message = message
                l.ref_object = self.ref_object.__class__.__name__ + " (" + str(self.ref_object.pk) + ")"
                l.type = 'None'
                l.level = int(level)
                l.spider_name = self.name
                l.scraper = self.scraper
                
                # Look for corresponding log markers
                lms = LogMarker.objects.filter(
                    Q(ref_object=l.ref_object) | Q(ref_object=''),
                    Q(spider_name=l.spider_name) | Q(spider_name=''),
                    Q(scraper=l.scraper) | Q(scraper__isnull=True),
                )
                for lm in lms:
                    if lm.message_contains in l.message:
                        if lm.custom_type:
                            l.type = lm.custom_type
                        else:
                            l.type = lm.get_mark_with_type_display()
                l.save()
                
                #Delete old logs
                if Log.objects.count() > self.conf['LOG_LIMIT']:
                    items = Log.objects.all()[self.conf['LOG_LIMIT']:]
                    for item in items:
                        item.delete()
        
        self.dds_logger.log(level, message)
        
    
