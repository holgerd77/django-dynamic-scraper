import os.path

from scrapy.exceptions import CloseSpider
from scraper.models import Event
from scraper.scraper_test import EventChecker, ScraperTest
from dynamic_scraper.models import SchedulerRuntime, Log

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


class CheckerRunTest(ScraperTest):
    
    def setUp(self):
        super(CheckerRunTest, self).setUp()
        
        self.scraper.checker_type = 'X'
        self.scraper.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.scraper.checker_x_path_result = u'Event was deleted!'
        self.scraper.checker_ref_url = u'http://localhost:8010/static/site_for_checker/event_not_found.html'
        self.scraper.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_for_checker/event1.html',
            checker_runtime=scheduler_rt)
        self.event.save()
    
    
    def test_checker_test_wrong_checker_config(self):
        self.scraper.checker_ref_url = ''
        self.scraper.save()
        
        self.assertRaises(CloseSpider, self.run_checker_test, 1)
    
    
    def test_none_type(self):
        self.scraper.checker_type = 'N'
        self.scraper.save()
        self.assertRaises(CloseSpider, self.run_event_checker, 1)
    
    
    def test_x_path_type_keep_video(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event1.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
    
    
    def test_x_path_type_404_delete(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_x_path_type_404_delete_with_zero_actions(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.save()
        
        self.event.checker_runtime.num_zero_actions = 3
        self.event.checker_runtime.save()
        
        kwargs = {
            'id': 1,
            'do_action': 'yes',
            'run_type': 'TASK',
        }
        checker = EventChecker(**kwargs)
        self.crawler.crawl(checker)
        self.crawler.start()
        
        self.assertEqual(len(Event.objects.all()), 1)
        
    
    def test_x_path_type_x_path_delete(self):
        
        self.event.url = 'http://localhost:8010/static/site_for_checker/event2.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
        
    
    def test_x_path_type_404_delete_with_img(self):
        path = os.path.join(self.PROJECT_ROOT, 'imgs/event_image.jpg')
        if not os.path.exists(path):
            file = open(path,"w")
            file.write('Let\s assume this is an image!')
            file.close()
        
        self.se_desc.mandatory = True
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.description = 'event_image.jpg'
        self.event.save()
        
        self.assertTrue(os.path.exists(path))
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)   
        self.assertFalse(os.path.exists(path))
    
    
    def test_404_type_404_delete(self):
        self.scraper.checker_type = '4'
        self.scraper.save()
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_404_type_x_path_delete(self):
        self.scraper.checker_type = '4'
        self.scraper.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
     