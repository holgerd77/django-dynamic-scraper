import os.path

from scraper.models import Event
from scraper.scraper_test import ScraperTest
from dynamic_scraper.models import SchedulerRuntime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


class CheckerRunTest(ScraperTest):
    
    def setUp(self):
        super(CheckerRunTest, self).setUp()
        
        self.scraper.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.scraper.checker_x_path_result = u'Event was deleted!'
        self.scraper.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_for_checker/event1.html',
            checker_runtime=scheduler_rt)
        self.event.save()
    
    
    def test_keep_video(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event1.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
    
    
    def test_404_delete(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
        
    
    def test_x_path_delete(self):
        
        self.event.url = 'http://localhost:8010/static/site_for_checker/event2.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
        
    
    def test_404_delete_with_img(self):
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
        
            
    