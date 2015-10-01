import os.path, unittest

from scrapy.exceptions import CloseSpider
from scraper.models import Event
from scraper.scraper_test import EventChecker, ScraperTest
from dynamic_scraper.models import Checker, Log, SchedulerRuntime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


class CheckerRunTest(ScraperTest):
    
    def setUp(self):
        super(CheckerRunTest, self).setUp()
        
        self.checker = Checker()
        self.checker.scraped_obj_attr = self.soa_url
        self.checker.scraper = self.scraper
        self.checker.checker_type = 'X'
        self.checker.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.checker.checker_x_path_result = u'Event was deleted!'
        self.checker.checker_ref_url = u'http://localhost:8010/static/site_for_checker/event_not_found.html'
        self.checker.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_for_checker/event1.html',
            checker_runtime=scheduler_rt)
        self.event.save()
    
    def setUpWithSecondChecker(self):
        self.checker2 = Checker()
        self.checker2.scraped_obj_attr = self.soa_url
        self.checker2.scraper = self.scraper
        self.checker2.checker_type = 'X'
        self.checker2.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.checker2.checker_x_path_result = u'Event was deleted!'
        self.checker2.checker_ref_url = u'http://localhost:8010/static/site_for_checker/event_not_found.html'
        self.checker2.save()
        
    
    def test_no_checker(self):
        self.checker.delete()
        self.assertRaises(CloseSpider, self.run_event_checker, 1)
    
    
    def test_x_path_type_keep(self):
        self.event.url = 'http://localhost:8010/static/site_for_checker/event1.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
    
    
    def test_x_path_type_keep_double(self):
        self.setUpWithSecondChecker()
        self.event.url = 'http://localhost:8010/static/site_for_checker/event1.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
    
    
    def test_x_path_type_blank_result_field_keep(self):
        self.scraper.checker_x_path_result = ''
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
    
    
    def test_x_path_type_x_path_first_delete_double(self):
        self.setUpWithSecondChecker()
        self.event.url = 'http://localhost:8010/static/site_for_checker/event2.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_x_path_type_x_path_second_delete_double(self):
        self.setUpWithSecondChecker()
        self.checker.checker_x_path = u'//div[@class="oh_my_wrong_xpath_for_delete"]/div/text()'
        self.checker.save()
        self.event.url = 'http://localhost:8010/static/site_for_checker/event2.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
        
    def test_x_path_type_blank_result_field_x_path_delete(self):
        self.scraper.checker_x_path_result = ''
        self.event.url = 'http://localhost:8010/static/site_for_checker/event2.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
    

    def _create_imgs_in_dirs(self, img_dirs):
        img_paths = []
        for img_dir in img_dirs:
            path = os.path.join(self.PROJECT_ROOT, img_dir, 'event_image.jpg')
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if not os.path.exists(path):
                file = open(path,"w")
                file.write('Let\s assume this is an image!')
                file.close()
            img_paths.append(path)
        return img_paths

    
    def _run_img_test_with_dirs(self, img_dirs):
        img_paths = self._create_imgs_in_dirs(img_dirs)

        self.se_desc.mandatory = True
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.description = 'event_image.jpg'
        self.event.save()

        for path in img_paths:
            self.assertTrue(os.path.exists(path))
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
        for path in img_paths:
            self.assertFalse(os.path.exists(path))


    def test_delete_with_img_flat_no_thumbs(self):
        img_dirs = ['imgs/',]
        self._run_img_test_with_dirs(img_dirs)


    def test_delete_with_img_flat_with_thumbs(self):
        img_dirs = ['imgs/',]
        self._run_img_test_with_dirs(img_dirs)


    def test_delete_with_img_all_no_thumbs(self):
        img_dirs = ['imgs/full/',]
        self._run_img_test_with_dirs(img_dirs)
    

    def test_delete_with_img_all_with_thumbs(self):
        img_dirs = ['imgs/full/', 'imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        self._run_img_test_with_dirs(img_dirs)


    def test_delete_with_img_thumbs_with_thumbs(self):
        img_dirs = ['imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        self._run_img_test_with_dirs(img_dirs)

    
    def test_404_type_404_delete(self):
        self.checker.checker_type = '4'
        self.checker.save()
        self.event.url = 'http://localhost:8010/static/site_for_checker/event_which_is_not_there.html'
        self.event.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)
    
    
    def test_404_type_x_path_delete(self):
        self.checker.checker_type = '4'
        self.checker.save()
        
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)


    @unittest.skip("Skipped, CloseSpider can't be catched from within test env, other option: direct access to Scrapy log strings.")
    def test_checker_test_wrong_checker_config(self):
        self.checker.checker_ref_url = ''
        self.checker.save()
        
        self.assertRaises(CloseSpider, self.run_checker_test(1))


     