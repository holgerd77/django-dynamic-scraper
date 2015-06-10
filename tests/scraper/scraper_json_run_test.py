import os.path, sys

from scrapy import log
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest



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
        self.se_url.x_path = u'json_url'
        self.se_url.save()
        self.se_desc.x_path = u'event_details.description'
        self.se_desc.from_detail_page = True
        self.se_desc.save()
        self.run_event_spider(1)
        #log.msg(unicode(Event.objects.all()), level=log.INFO)
        self.assertEqual(len(Event.objects.filter(description='Event Detail Page 1 Description')), 1)





