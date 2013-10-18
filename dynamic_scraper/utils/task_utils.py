import datetime, json
import urllib, urllib2, httplib
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from dynamic_scraper.models import Scraper

class TaskUtils():
    
    conf = {
        "MAX_SPIDER_RUNS_PER_TASK": 10,
        "MAX_CHECKER_RUNS_PER_TASK": 25,
    }
    
    def _run_spider(self, **kwargs):
        param_dict = {
            'project': 'default',
            'spider': kwargs['spider'],
            'id': kwargs['id'],
            'run_type': kwargs['run_type'],
            'do_action': kwargs['do_action']
        }
        params = urllib.urlencode(param_dict)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection("localhost:6800")
        conn.request("POST", "/schedule.json", params, headers)
        conn.getresponse()
    
    
    def _pending_jobs(self, spider):
        # Ommit scheduling new jobs if there are still pending jobs for same spider
        resp = urllib2.urlopen('http://localhost:6800/listjobs.json?project=default')
        data = json.load(resp)
        if 'pending' in data:
            for item in data['pending']:
                if item['spider'] == spider:
                    return True
        return False
    
    
    def run_spiders(self, ref_obj_class, scraper_field_name, runtime_field_name, spider_name, *args, **kwargs):
        filter_kwargs = {
            '%s__status' % scraper_field_name: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        for key in kwargs:
            filter_kwargs[key] = kwargs[key]
        
        max = settings.get('DSCRAPER_MAX_SPIDER_RUNS_PER_TASK', self.conf['MAX_SPIDER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(*args, **filter_kwargs).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(spider_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.pk, spider=spider_name, run_type='TASK', do_action='yes')
        

    def run_checkers(self, ref_obj_class, scraper_field_path, runtime_field_name, checker_name, *args, **kwargs):
        filter_kwargs = {
            '%s__status' % scraper_field_path: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        for key in kwargs:
            filter_kwargs[key] = kwargs[key]
         
        #for key in filter_kwargs:
        #    print "another keyword arg: %s: %s" % (key, filter_kwargs[key])
        
        exclude_kwargs = {
            '%s__checker_type' % scraper_field_path: 'N',
        }
        
        max = settings.get('DSCRAPER_MAX_CHECKER_RUNS_PER_TASK', self.conf['MAX_CHECKER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(*args, **filter_kwargs).exclude(**exclude_kwargs).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(checker_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.pk, spider=checker_name, run_type='TASK', do_action='yes')

