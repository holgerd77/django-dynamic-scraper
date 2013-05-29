import datetime, json
import urllib, urllib2, httplib
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from dynamic_scraper.models import Scraper
from scrapyd.config import Config
from ConfigParser import NoOptionError

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
        scrapyd_config = Config()
        try:
            scrapyd_url = scrapyd_config.get('url')
        except NoOptionError:
            scrapyd_url = "localhost:6800"

        params = urllib.urlencode(param_dict)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(scrapyd_url)
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
    
    
    def run_spiders(self, ref_obj_class, scraper_field_name, runtime_field_name, spider_name):
        
        kwargs = {
            '%s__status' % scraper_field_name: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        
        max = settings.get('DSCRAPER_MAX_SPIDER_RUNS_PER_TASK', self.conf['MAX_SPIDER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(**kwargs).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(spider_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.id, spider=spider_name, run_type='TASK', do_action='yes')
        

    def run_checkers(self, ref_obj_class, scraper_field_path, runtime_field_name, checker_name):
        
        kwargs = {
            '%s__status' % scraper_field_path: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now(),
        }
        kwargs2 = {
            '%s__checker_type' % scraper_field_path: 'N',
        }
        
        max = settings.get('DSCRAPER_MAX_CHECKER_RUNS_PER_TASK', self.conf['MAX_CHECKER_RUNS_PER_TASK'])
        ref_obj_list = ref_obj_class.objects.filter(**kwargs).exclude(**kwargs2).order_by('%s__next_action_time' % runtime_field_name)[:max]
        if not self._pending_jobs(checker_name):
            for ref_object in ref_obj_list:
                self._run_spider(id=ref_object.id, spider=checker_name, run_type='TASK', do_action='yes')


    def run_checker_tests(self):
        
        scraper_list = Scraper.objects.filter(checker_x_path__isnull=False, checker_x_path_result__isnull=False, checker_x_path_ref_url__isnull=False)

        for scraper in scraper_list:
            self._run_spider(id=scraper.id, spider='checker_test', run_type='TASK', do_action='yes')
