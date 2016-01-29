from __future__ import unicode_literals
import logging, os.path, random, unittest

from twisted.internet import reactor
from scrapy.exceptions import CloseSpider 

from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime, Log


class ScraperImgRunTest(ScraperTest):

    def process_image_test(self, expected_dirs, non_expected_dirs):
        imgs = [
            '1d7c0c2ea752d7aa951e88f2bc90a3f17058c473.jpg',
            '3cfa4d48e423c5eb3d4f6e9b5e5d373036ac5192.jpg',
        ]
        
        expected_paths = []
        for expected_dir in expected_dirs:
            for img in imgs:
                expected_paths.append(os.path.join(self.PROJECT_ROOT, expected_dir, img))
        non_expected_paths = []
        for non_expected_dir in non_expected_dirs:
            for img in imgs:
                non_expected_paths.append(os.path.join(self.PROJECT_ROOT, non_expected_dir, img))
        self.se_desc.mandatory = True
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_imgs/event_main.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(Event.objects.get(title='Event 1').description, imgs[0])
        for path in expected_paths:
            self.assertTrue(os.access(path, os.F_OK), "Expected image path {p} not found!".format(p=path))
        for path in non_expected_paths:
            self.assertFalse(os.access(path, os.F_OK), "Not expected image path {p} found!".format(p=path))
    
    
    def test_img_store_format_flat_no_thumbs(self):
        expected_dirs = ['imgs/',]
        non_expected_dirs = ['imgs/full/', 'imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        self.process_image_test(expected_dirs, non_expected_dirs)


    def test_img_store_format_flat_with_thumbs(self):
        expected_dirs = ['imgs/',]
        non_expected_dirs = ['imgs/full/', 'imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        self.process_image_test(expected_dirs, non_expected_dirs)
    

    def test_img_store_format_all_no_thumbs(self):
        expected_dirs = ['imgs/full/',]
        non_expected_dirs = ['imgs/', 'imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        self.process_image_test(expected_dirs, non_expected_dirs)
    

    def test_img_store_format_all_with_thumbs(self):
        expected_dirs = ['imgs/full/', 'imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        non_expected_dirs = ['imgs/',]
        self.process_image_test(expected_dirs, non_expected_dirs)
    

    def test_img_store_format_thumbs_with_thumbs(self):
        expected_dirs = ['imgs/thumbs/medium/', 'imgs/thumbs/small/',]
        non_expected_dirs = ['imgs/full/', 'imgs/',]
        self.process_image_test(expected_dirs, non_expected_dirs)


    def test_missing_img_when_img_field_not_mandatory(self):
        self.se_desc.mandatory = False
        self.se_desc.save()
        self.soa_desc.attr_type = 'I'
        self.soa_desc.save()
        
        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_imgs/event_main2.html')
        self.event_website.save()
        self.run_event_spider(1)
        
        self.assertEqual(len(Event.objects.all()), 1)

