import json, os

from jsonpath_rw import jsonpath, parse
from jsonpath_rw.lexer import JsonPathLexerError

from scrapy import log, signals
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.scheduler import Scheduler


class DjangoChecker(DjangoBaseSpider):
    
    name = "django_checker"


    def __init__(self, *args, **kwargs):
        super(DjangoChecker, self).__init__(self, *args, **kwargs)
        self._set_config(**kwargs)
        self._check_checker_config()
        
        self.start_urls.append(self.scrape_url)
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.checker_scheduler_conf)
        dispatcher.connect(self.response_received, signal=signals.response_received)
        
        msg = "Checker for " + self.ref_object.__class__.__name__ + " \"" + str(self.ref_object) + "\" (" + str(self.ref_object.pk) + ") initialized."
        self.log(msg, log.INFO)

    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(DjangoChecker, self)._set_config(log_msg, **kwargs)


    def _check_checker_config(self):
        if self.scraper.checker_type == 'N':
            msg = 'No checker defined for scraper!'
            log.msg(msg, log.WARNING)
            raise CloseSpider(msg)


    def _del_ref_object(self):
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        
        try:
            img_elem = self.scraper.get_image_elem()
            if hasattr(self.ref_object, img_elem.scraped_obj_attr.name):
                img_name = getattr(self.ref_object, img_elem.scraped_obj_attr.name)

                thumb_paths = []
                if settings.get('IMAGES_THUMBS') and len(settings.get('IMAGES_THUMBS')) > 0:
                    for key in settings.get('IMAGES_THUMBS').iterkeys():
                        thumb_paths.append(('thumbnail, %s' % key, os.path.join(settings.get('IMAGES_STORE'), 'thumbs', key, img_name),))

                del_paths = []
                if self.conf['IMAGES_STORE_FORMAT'] == 'FLAT':
                    del_paths.append(('original, flat path', os.path.join(settings.get('IMAGES_STORE'), img_name),))
                if self.conf['IMAGES_STORE_FORMAT'] == 'ALL':
                    del_paths.append(('original, full/ path', os.path.join(settings.get('IMAGES_STORE'), 'full' , img_name),))
                    del_paths += thumb_paths
                if self.conf['IMAGES_STORE_FORMAT'] == 'THUMBS':
                    del_paths += thumb_paths

                for path in del_paths:
                    if os.access(path[1], os.F_OK):
                        try:
                            os.unlink(path[1])
                            self.log("Associated image (%s, %s) deleted." % (img_name, path[0]), log.INFO)
                        except Exception:
                            self.log("Associated image (%s, %s) could not be deleted!" % (img_name, path[0]), log.ERROR)
                    else:
                        self.log("Associated image (%s, %s) could not be found!" % (img_name, path[0]), log.WARNING)
        except ScraperElem.DoesNotExist:
            pass
        
        self.ref_object.delete()
        self.action_successful = True
        self.log("Item deleted.", log.INFO)


    def start_requests(self):
        for url in self.start_urls:
            meta = {}
            if self.scraper.detail_page_content_type == 'H' and self.scraper.render_javascript:
                meta['splash'] = {
                    'endpoint': 'render.html',
                    'args': self.conf['SPLASH_ARGS'].copy()
                }
            yield Request(url, self.parse, meta=meta)


    def response_received(self, **kwargs):
        # 404 test
        if kwargs['response'].status == 404:
            
            if self.scheduler_runtime.num_zero_actions == 0:
                self.log("Checker test returned second 404.", log.INFO)
                if self.conf['DO_ACTION']:
                    self._del_ref_object()
            else:
                self.log("Checker test returned first 404.", log.INFO)
                self.action_successful = True


    def parse(self, response):
        # x_path test
        if self.scraper.checker_type == '4':
            self.log("No 404. Item kept.", log.INFO)
            return
        if self.scraper.detail_page_content_type == 'J':
            json_resp = json.loads(response.body_as_unicode())
            try:
                jsonpath_expr = parse(self.scraper.checker_x_path)
            except JsonPathLexerError:
                raise CloseSpider("Invalid checker JSONPath!")
            test_select = [match.value for match in jsonpath_expr.find(json_resp)]
            #self.log(unicode(test_select), log.INFO)
        else:
            try:
                test_select = response.xpath(self.scraper.checker_x_path).extract()
            except ValueError:
                self.log('Invalid checker XPath!', log.ERROR)
                return
        
        if len(test_select) > 0 and self.scraper.checker_x_path_result == '':
            self.log("Elements for XPath found on page (no result string defined).", log.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
        elif len(test_select) > 0 and test_select[0] == self.scraper.checker_x_path_result:
            self.log("XPath result string '" + self.scraper.checker_x_path_result + "' found on page.", log.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
        else:
            self.log("XPath result string not found. Item kept.", log.INFO)
            return
