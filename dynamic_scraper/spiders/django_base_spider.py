import datetime, json, os
from scrapy import log, signals
from scrapy.spider import Spider
from scrapy.contrib.spiders import CrawlSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import CloseSpider

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from dynamic_scraper.models import Log, LogMarker


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
        "LOG_ENABLED": True,
        "LOG_LEVEL": 'ERROR',
        "LOG_LIMIT": 250,
    }

    mp_request_kwargs = {}
    dp_request_kwargs = {}

    command  = 'scrapy crawl SPIDERNAME -a id=REF_OBJECT_ID '
    command += '[-a do_action=(yes|no) -a run_type=(TASK|SHELL)'
    command += ' -a max_items_read={Int} -a max_items_save={Int}]'
    
    
    def __init__(self, *args, **kwargs):
        msg = "Django settings used: %s" % os.environ.get("DJANGO_SETTINGS_MODULE")
        log.msg(msg, log.INFO)
        
        super(DjangoBaseSpider,  self).__init__(None, **kwargs)
        
        self._check_mandatory_vars()


    def _set_ref_object(self, ref_object_class, **kwargs):
        if not 'id' in kwargs:
            msg = "You have to provide an ID (Command: %s)." % self.command
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)
        try:
            self.ref_object = ref_object_class.objects.get(pk=kwargs['id'])
        except ObjectDoesNotExist:
            msg = "Object with ID " + kwargs['id'] + " not found (Command: %s)." % self.command
            log.msg(msg, log.ERROR)
            raise CloseSpider(msg)


    def _set_config(self, log_msg, **kwargs):
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()

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
        
        self.conf['SPLASH_ARGS'] = settings.get('DSCRAPER_SPLASH_ARGS', self.conf['SPLASH_ARGS'])  
        if 'wait' not in self.conf['SPLASH_ARGS']:
            self.conf['SPLASH_ARGS']['wait'] = 0.5

        self.conf['IMAGES_STORE_FORMAT'] = settings.get('DSCRAPER_IMAGES_STORE_FORMAT', self.conf['IMAGES_STORE_FORMAT'])
        if self.conf["IMAGES_STORE_FORMAT"] == 'FLAT':
            msg = "Use simplified FLAT images store format (save the original or one thumbnail image)"
            log.msg(msg, log.INFO)
            if settings.get('IMAGES_THUMBS') and len(settings.get('IMAGES_THUMBS')) > 0:
                msg = "IMAGES_THUMBS setting found, saving images as thumbnail images with size %s (first entry)" % settings.get('IMAGES_THUMBS').iterkeys().next()
            else:
                msg = "IMAGES_THUMBS setting not found, saving images with original size"
            log.msg(msg, log.INFO)
        elif self.conf["IMAGES_STORE_FORMAT"] == 'ALL':
            msg = "Use ALL images store format (Scrapy behaviour, save both original and thumbnail images)"
            log.msg(msg, log.INFO)
        else:
            msg = "Use THUMBS images store format (save only the thumbnail images)"
            log.msg(msg, log.INFO)

        self.conf['LOG_ENABLED'] = settings.get('DSCRAPER_LOG_ENABLED', self.conf['LOG_ENABLED'])
        self.conf['LOG_LEVEL'] = settings.get('DSCRAPER_LOG_LEVEL', self.conf['LOG_LEVEL'])
        self.conf['LOG_LIMIT'] = settings.get('DSCRAPER_LOG_LIMIT', self.conf['LOG_LIMIT'])
        self.log("Runtime config: " + log_msg, log.INFO)
        
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)


    def _check_mandatory_vars(self):
        if self.conf['RUN_TYPE'] == 'TASK':
            if not getattr(self, 'scheduler_runtime', None):
                msg = "You have to provide a scheduler_runtime when running with run_type TASK."
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)
            msg = "SchedulerRuntime (" + str(self.scheduler_runtime) + ") found."
            self.log(msg, log.INFO)
        
        for var in self.mandatory_vars:
            attr = getattr(self, var, None)
            if not attr:
                msg = "Missing attribute %s (Command: %s)." % (var, self.command)
                log.msg(msg, log.ERROR)
                raise CloseSpider(msg)
            
        if self.scraper.status == 'P' or self.scraper.status == 'I':
            msg = 'Scraper status set to %s!' % (self.scraper.get_status_display())
            self.log(msg, log.WARNING)
            raise CloseSpider(msg)


    def _set_request_kwargs(self):
        try:
            self.scraper.get_main_page_rpt()
        except ObjectDoesNotExist:
            raise CloseSpider("Scraper must have exactly one main page request page type!")

        for rpt in self.scraper.requestpagetype_set.all():
            if rpt.page_type == 'MP':
                pt_dict = self.mp_request_kwargs
            else:
                self.dp_request_kwargs[rpt.page_type] = {}
                pt_dict = self.dp_request_kwargs[rpt.page_type]

            if rpt.headers != u'':
                try:
                    headers = json.loads(rpt.headers)
                except ValueError:
                    raise CloseSpider("Incorrect HTTP header attribute (%s): not a valid JSON dict!" % rpt.page_type)
                if not isinstance(headers, dict):
                    raise CloseSpider("Incorrect HTTP header attribute (%s): not a valid JSON dict!" % rpt.page_type)
                pt_dict['headers'] = headers

            if rpt.body != u'':
                pt_dict['body'] = rpt.body

            if rpt.cookies != u'':
                try:
                    cookies = json.loads(rpt.cookies)
                except ValueError:
                    raise CloseSpider("Incorrect cookies attribute (%s): not a valid JSON dict!" % rpt.page_type)
                if not isinstance(cookies, dict):
                    raise CloseSpider("Incorrect cookies attribute (%s): not a valid JSON dict!" % rpt.page_type)
                pt_dict['cookies'] = cookies

            if rpt.meta != u'':
                try:
                    meta = json.loads(rpt.meta)
                except ValueError:
                    raise CloseSpider("Incorrect meta attribute (%s): not a valid JSON dict!" % rpt.page_type)
                if not isinstance(meta, dict):
                    raise CloseSpider("Incorrect meta attribute (%s): not a valid JSON dict!" % rpt.page_type)
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
            msg += "%s, " % str(self.scheduler_runtime.next_action_time.strftime("%Y-%m-%d %H:%m"))
            msg += "Next action factor: %s, " % str(self.scheduler_runtime.next_action_factor)
            msg += "Zero actions: %s)" % str(self.scheduler_runtime.num_zero_actions)
            self.log(msg, log.INFO)
    
    
    def log(self, message, level=log.DEBUG):
        if self.conf['RUN_TYPE'] == 'TASK' and self.conf['DO_ACTION']:
            
            if self.conf['LOG_ENABLED'] and level >= Log.numeric_level(self.conf['LOG_LEVEL']):
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
                
        super(DjangoBaseSpider, self).log(message, level)
        
    
