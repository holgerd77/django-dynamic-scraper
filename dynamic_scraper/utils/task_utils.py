import datetime
import urllib, httplib
from dynamic_scraper.models import Scraper

class TaskUtils():
    
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
    
    
    def run_spiders(self, ref_obj_class, scraper_field_name, runtime_field_name, spider_name):
        
        kwargs = {
            '%s__status' % scraper_field_name: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now,
        }
        
        ref_obj_list = ref_obj_class.objects.filter(**kwargs)
        for ref_object in ref_obj_list:
            self._run_spider(id=ref_object.id, spider=spider_name, run_type='TASK', do_action='yes')
        

    def run_checkers(self, ref_obj_class, scraper_field_path, runtime_field_name, checker_name):
        
        kwargs = {
            '%s__status' % scraper_field_path: 'A',
            '%s__next_action_time__lt' % runtime_field_name: datetime.datetime.now,
        }
        kwargs2 = {
            '%s__checker_type' % scraper_field_path: 'N',
        }
        
        ref_obj_list = ref_obj_class.objects.filter(**kwargs).exclude(**kwargs2)
        for ref_object in ref_obj_list:
            self._run_spider(id=ref_object.id, spider=checker_name, run_type='TASK', do_action='yes')


    def run_checker_tests(self):
        
        scraper_list = Scraper.objects.filter(checker_x_path__isnull=False, checker_x_path_result__isnull=False, checker_x_path_ref_url__isnull=False)

        for scraper in scraper_list:
            self._run_spider(id=scraper.id, spider='checker_test', run_type='TASK', do_action='yes')