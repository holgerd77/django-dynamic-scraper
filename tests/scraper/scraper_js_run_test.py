import os
from scrapy.exceptions import CloseSpider 
from scraper.models import Event
from scraper.scraper_test import EventSpider, ScraperTest
from dynamic_scraper.models import SchedulerRuntime


class ScraperJSRunTest(ScraperTest):
    
    def setUpScraperJSDefaultScraper(self):
        self.event_website.url = os.path.join('http://localhost:8010/static/', 'site_with_js/event_main.html')
        self.event_website.save()

    def setUpScraperJSDockerScraper(self):
        self.event_website.url = os.path.join('http://10.0.2.2:8010/static/', 'site_with_js/event_main_docker.html')
        self.event_website.save()
        self.rpt_mp.render_javascript = True
        self.rpt_mp.dont_filter = True
        self.rpt_mp.save()
        self.rpt_dp1.render_javascript = True
        self.rpt_dp1.dont_filter = True
        self.rpt_dp1.save()

    def setUpScraperJSChecker(self, path):
        super(ScraperJSRunTest, self).setUp()

        self.scraper.checker_type = 'X'
        self.scraper.checker_x_path = u'//div[@class="event_not_found"]/div/text()'
        self.scraper.checker_ref_url = u'%ssite_with_js/event_not_found.html' % path
        self.scraper.save()
        
        scheduler_rt = SchedulerRuntime()
        scheduler_rt.save()
        
        self.event = Event(title='Event 1', event_website=self.event_website,
            description='Event 1 description', 
            url='%ssite_with_js/event_not_found.html' % path,
            checker_runtime=scheduler_rt)
        self.event.save()

    def setUpScraperJSDefaultChecker(self):
        self.setUpScraperJSChecker('http://localhost:8010/static/')
    
    def setUpScraperJSDockerChecker(self):
        self.setUpScraperJSChecker('http://10.0.2.2:8010/static/')
        self.rpt_dp1.render_javascript = True
        self.rpt_dp1.save()
    


    def test_default_no_scrapyjs_main_page(self):
        self.setUpScraperJSDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 1)

    def test_default_no_scrapyjs_detail_page(self):
        self.setUpScraperJSDefaultScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(description='Event 1 description')), 1)

    def test_activated_scrapyjs_main_page(self):
        self.setUpScraperJSDockerScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 2)

    def test_activated_scrapyjs_detail_page(self):
        self.setUpScraperJSDockerScraper()
        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.filter(description='Event 1 JS description')), 1)

    def test_only_main_page_scrapyjs_main_page(self):
        self.setUpScraperJSDockerScraper()
        self.event_website.url = os.path.join('http://10.0.2.2:8010/static/', 'site_with_js/event_main.html')
        self.event_website.save()
        self.rpt_dp1.render_javascript = False
        self.rpt_dp1.save()

        self.run_event_spider(1)
        self.assertEqual(len(Event.objects.all()), 2)
        self.assertEqual(len(Event.objects.filter(description='Event 1 description')), 1)
        self.assertEqual(len(Event.objects.filter(description='Event 1 JS description')), 0)

    def test_default_no_scrapyjs_checker_delete(self):
        self.setUpScraperJSDefaultChecker()
        self.scraper.checker_x_path_result = u'Event not found'
        self.scraper.save()

        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)

    def test_default_no_scrapyjs_checker_no_delete(self):
        self.setUpScraperJSDefaultChecker()
        self.scraper.checker_x_path_result = u'Event JS not found'
        self.scraper.save()

        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)

    def test_activated_scrapyjs_checker_delete(self):
        self.setUpScraperJSDockerChecker()
        self.scraper.checker_x_path_result = u'Event JS not found'
        self.scraper.save()

        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 0)

    def test_activated_scrapyjs_checker_no_delete(self):
        self.setUpScraperJSDockerChecker()
        self.scraper.checker_x_path_result = u'Event not found'
        self.scraper.save()

        self.run_event_checker(1)
        self.assertEqual(len(Event.objects.all()), 1)
