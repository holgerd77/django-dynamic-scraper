import os.path, sys

from scrapy import log
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime


class ScraperJSONRunTest(ScraperTest):

    def setUpScraperJSONDefaultScraper(self):
        self.se_base.x_path = u'response.events'
        self.se_base.save()
        self.se_title.x_path = u'title'
        self.se_title.save()
        self.se_url.x_path = u'url'
        self.se_url.save()
        self.se_desc.x_path = u'description'
        self.se_desc.from_detail_page = False
        self.se_desc.save()

        self.scraper.content_type = 'J'
        self.scraper.save()

        self.event_website.url = os.path.join(self.SERVER_URL, 'site_with_json_content_type/event_main.json')
        self.event_website.save()

    def extraSetUpHTMLChecker(self):
        self.scraper.checker_type = 'X'
        self.scraper.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.scraper.checker_x_path_result = u'Event not found!'
        self.scraper.checker_ref_url = u'http://localhost:8010/static/site_with_json_content_type/event_not_found.html'
        self.scraper.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_with_json_content_type/event_not_found.html',
            checker_runtime=scheduler_rt)
        self.event.save()

    def extraSetUpJSONChecker(self):
        self.scraper.detail_page_content_type = 'J'
        self.scraper.checker_type = 'X'
        self.scraper.checker_x_path = u'event_not_found'
        self.scraper.checker_x_path_result = u'Event not found!'
        self.scraper.checker_ref_url = u'http://localhost:8010/static/site_with_json_content_type/event_not_found.json'
        self.scraper.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='http://localhost:8010/static/site_with_json_content_type/event_not_found.json',
            checker_runtime=scheduler_rt)
        self.event.save()


    def test_num_scraped_objects(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        #log.msg(unicode(Event.objects.all()), level=log.INFO)
        self.assertEqual(len(Event.objects.all()), 3)


    def test_non_repetition(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(title='Event 1')), 1)


    def test_non_data_mixing(self):
        self.setUpScraperJSONDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(Event.objects.get(pk=1).title, 'Event 1')
        self.assertEqual(Event.objects.get(pk=1).description, 'Event 1 Description')


    def test_detail_page(self):
        self.setUpScraperJSONDefaultScraper()
        self.se_desc.x_path = u'//div/div[@class="description"]/text()'
        self.se_desc.from_detail_page = True
        self.se_desc.save()
        self.run_event_spider(1)
        #log.msg(unicode(Event.objects.all()), level=log.INFO)
        self.assertEqual(len(Event.objects.filter(description='Event Detail Page 1 Description')), 1)


    def test_detail_page_json(self):
        self.setUpScraperJSONDefaultScraper()
        self.scraper.detail_page_content_type = 'J'
        self.scraper.save()
        self.se_url.x_path = u'json_url'
        self.se_url.save()
        self.se_desc.x_path = u'event_details.description'
        self.se_desc.from_detail_page = True
        self.se_desc.save()
        self.run_event_spider(1)
        #log.msg(unicode(Event.objects.all()), level=log.INFO)
        self.assertEqual(len(Event.objects.filter(description='Event Detail Page 1 Description')), 1)


    def test_checker_x_path_type_x_path_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpHTMLChecker()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)


    def test_checker_x_path_type_x_path_no_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpHTMLChecker()
        self.scraper.checker_x_path = u'//div[@class="this_is_the_wrong_xpath"]/div/text()'
        self.scraper.save()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)


    def test_json_checker_x_path_type_x_path_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpJSONChecker()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)


    def test_json_checker_x_path_type_x_path_no_delete(self):
        self.setUpScraperJSONDefaultScraper()
        self.extraSetUpJSONChecker()
        self.scraper.checker_x_path = u'this_is_the_wrong_xpath'
        self.scraper.save()
        self.assertEqual(len(Event.objects.all()), 1)
        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)





