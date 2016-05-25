#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from builtins import str
import datetime, json, logging, os

from jsonpath_rw import jsonpath, parse
from jsonpath_rw.lexer import JsonPathLexerError

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from pydispatch import dispatcher

from django.utils import timezone

from dynamic_scraper.spiders.django_base_spider import DjangoBaseSpider
from dynamic_scraper.models import ScraperElem
from dynamic_scraper.utils.scheduler import Scheduler


class DjangoChecker(DjangoBaseSpider):
    
    name = "django_checker"
    mandatory_vars = ['ref_object', 'scraper',]


    def __init__(self, *args, **kwargs):
        super(DjangoChecker, self).__init__(self, *args, **kwargs)
        self._set_config(**kwargs)
        self._check_checker_config()
        self._set_request_kwargs()
        self._set_meta_splash_args()
        
        self.scheduler = Scheduler(self.scraper.scraped_obj_class.checker_scheduler_conf)
        dispatcher.connect(self.response_received, signal=signals.response_received)
        
        msg = "Checker for " + self.ref_object.__class__.__name__ + " \"" + str(self.ref_object) + "\" (" + str(self.ref_object.pk) + ") initialized."
        self.log(msg, logging.INFO)

    
    def _set_config(self, **kwargs):
        log_msg = ""
        super(DjangoChecker, self)._set_config(log_msg, **kwargs)


    def _check_checker_config(self):
        if self.scraper.checker_set.count() == 0:
            msg = 'No checkers defined for scraper!'
            logging.warning(msg)
            raise CloseSpider(msg)


    def _del_ref_object(self):
        if self.action_successful:
            self.log("Item already deleted, skipping.", logging.INFO)
            return
        
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        
        try:
            img_elem = self.scraper.get_image_elem()
            if hasattr(self.ref_object, img_elem.scraped_obj_attr.name):
                img_name = getattr(self.ref_object, img_elem.scraped_obj_attr.name)

                thumb_paths = []
                if settings.get('IMAGES_THUMBS') and len(settings.get('IMAGES_THUMBS')) > 0:
                    for key in settings.get('IMAGES_THUMBS').keys():
                        thumb_paths.append(('thumbnail, {k}'.format(k=key), os.path.join(settings.get('IMAGES_STORE'), 'thumbs', key, img_name),))

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
                            self.log("Associated image ({n}, {p}) deleted.".format(n=img_name, p=path[0]), logging.INFO)
                        except Exception:
                            self.log("Associated image ({n}, {p}) could not be deleted!".format(n=img_name, p=path[0]), logging.ERROR)
                    else:
                        self.log("Associated image ({n}, {p}) could not be found!".format(n=img_name, p=path[0]), logging.WARNING)
        except ScraperElem.DoesNotExist:
            pass
        
        self.ref_object.delete()
        self.scraper.last_checker_delete = timezone.now()
        self.scraper.save()
        self.action_successful = True
        self.log("Item deleted.", logging.INFO)


    def start_requests(self):
        for checker in self.scraper.checker_set.all():
            url = getattr(self.ref_object, checker.scraped_obj_attr.name)
            rpt = self.scraper.get_rpt_for_scraped_obj_attr(checker.scraped_obj_attr)
            kwargs = self.dp_request_kwargs[rpt.page_type].copy()
            if 'meta' not in kwargs:
                kwargs['meta'] = {}
            kwargs['meta']['checker'] = checker
            kwargs['meta']['rpt'] = rpt
            self._set_meta_splash_args()
            if url:
                if rpt.request_type == 'R':
                    yield Request(url, callback=self.parse, method=rpt.method, dont_filter=True, **kwargs)
                else:
                    yield FormRequest(url, callback=self.parse, method=rpt.method, formdata=self.dp_form_data[rpt.page_type], dont_filter=True, **kwargs)


    def response_received(self, **kwargs):
        checker = kwargs['response'].request.meta['checker']
        rpt = kwargs['response'].request.meta['rpt']
        # 404 test
        if kwargs['response'].status == 404:
            
            if self.scheduler_runtime.num_zero_actions == 0:
                self.log("Checker test returned second 404 ({c}). Delete reason.".format(c=str(checker)), logging.INFO)
                if self.conf['DO_ACTION']:
                    self._del_ref_object()
            else:
                self.log("Checker test returned first 404 ({c}).".format(str(checker)), logging.INFO)
                self.action_successful = True


    def parse(self, response):
        # x_path test
        checker = response.request.meta['checker']
        rpt = response.request.meta['rpt']
        if checker.checker_type == '4':
            self.log("No 404 ({c}).".format(c=str(checker)), logging.INFO)
            return
        if rpt.content_type == 'J':
            json_resp = json.loads(response.body_as_unicode())
            try:
                jsonpath_expr = parse(checker.checker_x_path)
            except JsonPathLexerError:
                raise CloseSpider("Invalid checker JSONPath ({c})!".format(c=str(checker)))
            test_select = [match.value for match in jsonpath_expr.find(json_resp)]
            #self.log(unicode(test_select), logging.INFO)
        else:
            try:
                test_select = response.xpath(checker.checker_x_path).extract()
            except ValueError:
                self.log("Invalid checker XPath ({c})!".format(c=str(checker)), logging.ERROR)
                return
        
        if len(test_select) > 0 and checker.checker_x_path_result == '':
            self.log("Elements for XPath found on page (no result string defined) ({c}). Delete reason.".format(c=str(checker)), logging.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
        elif len(test_select) > 0 and test_select[0] == checker.checker_x_path_result:
            self.log("XPath result string '{s}' found on page ({c}). Delete reason.".format(s=checker.checker_x_path_result, c=str(checker)), logging.INFO)
            if self.conf['DO_ACTION']:
                self._del_ref_object()
            return
        else:
            self.log("XPath result string not found ({c}).".format(c=str(checker)), logging.INFO)
            return
    
