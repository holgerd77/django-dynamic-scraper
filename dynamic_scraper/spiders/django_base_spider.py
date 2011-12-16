import datetime
from scrapy import log, signals
from scrapy.spider import BaseSpider
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import CloseSpider

from django.core.exceptions import ObjectDoesNotExist


class DjangoBaseSpider(BaseSpider):
    
    name = None
    action_successful = False
    allowed_domains = []
    start_urls = []
    conf = {
        "DO_ACTION": False,
        "RUN_TYPE": 'SHELL',
    }
    command = 'scrapy crawl SPIDERNAME -a id=REF_OBJECT_ID [-a do_action=(yes|no) -a run_type=(TASK|SHELL)]'
    
    
    def _check_mandatory_vars(self, mandatory_vars):
        mandatory_vars.append('ref_object')
        mandatory_vars.append('scheduler_runtime')
        for var in mandatory_vars:
            if not hasattr(self, var):
                raise CloseSpider("Missing attribute %s (Command: %s)." % var % self.command)
    
    
    def _set_conf(self, **kwargs):
        if 'run_type' in kwargs:
            self.conf['RUN_TYPE'] = kwargs['run_type']
        if 'do_action' in kwargs:
            if kwargs['do_action'] == 'yes':
                self.conf['DO_ACTION'] = True
            else:
                self.conf['DO_ACTION'] = False
        self.pre_log_msg = "[" + self.ref_object.__class__.__name__ + "(" + str(self.ref_object.id)  + ")] "
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
                
    
    def _set_ref_object(self, ref_object_class, **kwargs):
        if not 'id' in kwargs:
            raise CloseSpider("You have to provide an ID (Command: %s)." % self.command)
        try:
            self.ref_object = ref_object_class.objects.get(id=kwargs['id'])
        except ObjectDoesNotExist:
            raise CloseSpider("Object with ID " + kwargs['id'] + " not found (Command: %s)." % self.command)
    
    
    def spider_closed(self):
        if self.conf['RUN_TYPE'] == 'TASK' and self.conf['DO_ACTION']:
            
            time_delta, factor, num_crawls = self.scheduler.calc_next_action_time(\
                    self.action_successful,\
                    self.scheduler_runtime.next_crawl_factor,\
                    self.scheduler_runtime.num_zero_crawls)
            self.scheduler_runtime.next_crawl_time = datetime.datetime.now() + time_delta
            self.scheduler_runtime.next_crawl_factor = factor
            self.scheduler_runtime.num_zero_crawls = num_crawls
            self.scheduler_runtime.save()
        
        if hasattr(self, 'scraper_runtime'):
            self.scraper_runtime.save()
    
    
    def log(self, message, level=log.DEBUG):
        message = self.pre_log_msg + message
        super(DjangoBaseSpider, self).log(message, level)
        
    