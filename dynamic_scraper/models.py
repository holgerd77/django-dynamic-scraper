#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from builtins import range
from builtins import str
from builtins import object
import datetime
from django.db import models
from django.db.models import Q


@python_2_unicode_compatible
class ScrapedObjClass(models.Model):
    name = models.CharField(max_length=200)
    scraper_scheduler_conf = models.TextField(default='\
"MIN_TIME": 15,\n\
"MAX_TIME": 10080,\n\
"INITIAL_NEXT_ACTION_FACTOR": 10,\n\
"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n\
"FACTOR_CHANGE_FACTOR": 1.3,\n')
    checker_scheduler_conf = models.TextField(default='\
"MIN_TIME": 1440,\n\
"MAX_TIME": 10080,\n\
"INITIAL_NEXT_ACTION_FACTOR": 1,\n\
"ZERO_ACTIONS_FACTOR_CHANGE": 5,\n\
"FACTOR_CHANGE_FACTOR": 1.3,\n')
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = "Scraped object class"
        verbose_name_plural = "Scraped object classes"
        ordering = ['name',]


@python_2_unicode_compatible
class ScrapedObjAttr(models.Model):
    ATTR_TYPE_CHOICES = (
        ('S', 'STANDARD'),
        ('T', 'STANDARD (UPDATE)'),
        ('B', 'BASE'),
        ('U', 'DETAIL_PAGE_URL'),
        ('I', 'IMAGE'),
    )
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=100)
    obj_class = models.ForeignKey(ScrapedObjClass)
    attr_type = models.CharField(max_length=1, choices=ATTR_TYPE_CHOICES)
    id_field = models.BooleanField(default=False)
    save_to_db = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name + " (" + str(self.obj_class) + ")"
    
    class Meta(object):
        ordering = ['order',]


@python_2_unicode_compatible
class Scraper(models.Model):
    STATUS_CHOICES = (
        ('A', 'ACTIVE'),
        ('M', 'MANUAL'),
        ('P', 'PAUSED'),
        ('I', 'INACTIVE'),
    )
    WORK_STATUS_CHOICES = (
        ('R2', 'REVISION NEEDED (MAJOR)'),
        ('R1', 'REVISION NEEDED (MINOR)'),
        ('BR', 'BROKEN'),
        ('W', 'WORKING'),
        ('RC', 'RELEASE CANDIDATE'),
        ('BE', 'BETA'),
        ('A', 'ALPHA'),
        ('D', 'DRAFT'),
        ('S', 'SUSPENDED'),
        ('U', 'UNKNOWN'),
        ('N', 'NOT SET'),
    )
    CONTENT_TYPE_CHOICES = (
        ('H', 'HTML'),
        ('X', 'XML'),
        ('J', 'JSON'),
    )
    REQUEST_TYPE_CHOICES = (
        ('R', 'Request'),
        ('F', 'FormRequest'),
    )
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )
    PAGINATION_TYPE = (
        ('N', 'NONE'),
        ('R', 'RANGE_FUNCT'),
        ('F', 'FREE_LIST'),
    )
    name = models.CharField(max_length=200)
    scraped_obj_class = models.ForeignKey(ScrapedObjClass)
    help_text = "Runtime status of the scraper, used by scheduling mechanism."
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', help_text=help_text)
    help_text = "Internal work/progress status of the scraper."
    work_status = models.CharField(max_length=2, choices=WORK_STATUS_CHOICES, default='N', help_text=help_text)
    help_text = "Optional owner when working on scrapers with various people"
    owner = models.CharField(max_length=12, blank=True, help_text=help_text)
    max_items_read = models.IntegerField(blank=True, null=True, help_text="Max number of items to be read (empty: unlimited).")
    max_items_save = models.IntegerField(blank=True, null=True, help_text="Max number of items to be saved (empty: unlimited).")
    pagination_type = models.CharField(max_length=1, choices=PAGINATION_TYPE, default='N')
    pagination_on_start = models.BooleanField(default=False)
    pagination_append_str = models.CharField(max_length=200, blank=True, help_text="Syntax: /somepartofurl/{page}/moreurlstuff.html")
    pagination_page_replace = models.TextField(blank=True, 
        help_text="RANGE_FUNCT: uses Python range funct., syntax: [start], stop[, step], FREE_LIST: 'Replace text 1', 'Some other text 2', 'Maybe a number 3', ...")
    last_scraper_save_alert_period = models.CharField(max_length=5, blank=True, 
        help_text="Optional, used for scraper monitoring with 'check_last_scraper_saves' management cmd, \
        syntax: [HOURS]h or [DAYS]d or [WEEKS]w (e.g. '6h', '5d', '2w')")
    next_last_scraper_save_alert = models.DateTimeField(default=datetime.datetime.now,
        help_text="Next time the last scraper save will be alerted, normally set on management cmd run.",)
    last_checker_delete_alert_period = models.CharField(max_length=5, blank=True, 
        help_text="Optional, used for scraper monitoring with 'check_last_checker_deletes' management cmd, \
        syntax: [HOURS]h or [DAYS]d or [WEEKS]w (e.g. '6h', '5d', '2w')")
    next_last_checker_delete_alert = models.DateTimeField(default=datetime.datetime.now,
        help_text="Next time the last checker delete will be alerted, normally set on management cmd run.",)
    comments = models.TextField(blank=True)
    last_scraper_save = models.DateTimeField(null=True, blank=True)
    last_checker_delete = models.DateTimeField(null=True, blank=True)
    
    def get_alert_period_timedelta(self, attribute_str):
        if getattr(self, attribute_str) and len(getattr(self, attribute_str)) >= 2:
            period_str = getattr(self, attribute_str)[-1]
            num_str = getattr(self, attribute_str)[:-1]
            if period_str in ('h', 'd', 'w',):
                try:
                    num_int = int(num_str)
                    if period_str == 'h':
                        return datetime.timedelta(0, 0, 0, 0, 0, num_int)
                    if period_str == 'd':
                        return datetime.timedelta(num_int)
                    if period_str == 'w':
                        return datetime.timedelta(0, 0, 0, 0, 0, 0, num_int)
                except ValueError:
                    return None
            else:
                return None
        else:
            return None
    
    def get_last_scraper_save_alert_period_timedelta(self):
        return self.get_alert_period_timedelta('last_scraper_save_alert_period')
    
    def get_last_checker_delete_alert_period_timedelta(self):
        return self.get_alert_period_timedelta('last_checker_delete_alert_period')
    
    def get_main_page_rpt(self):
        return self.requestpagetype_set.get(page_type='MP')

    def get_detail_page_rpts(self):
        return s.requestpagetype_set.filter(~Q(page_type='MP'))

    def get_rpt(self, page_type):
        return self.requestpagetype_set.get(page_type=page_type)

    def get_rpt_for_scraped_obj_attr(self, soa):
        return self.requestpagetype_set.get(scraped_obj_attr=soa)

    def get_base_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='B')
    
    def get_base_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='B')
    
    def get_detail_page_url_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='U')

    def get_detail_page_url_id_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='U', scraped_obj_attr__id_field=True)
    
    def get_standard_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='T')
        return self.scraperelem_set.filter(q1 | q2)

    def get_id_field_elems(self):
        q1 = Q(scraped_obj_attr__id_field=True)
        return self.scraperelem_set.filter(q1)

    def get_standard_fixed_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='S')

    def get_standard_update_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='T')

    def get_standard_update_elems_from_detail_pages(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='T').filter(~Q(request_page_type='MP'))
    
    def get_image_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='I')
    
    def get_image_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='I')
    
    def get_scrape_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='T')
        q3 = Q(scraped_obj_attr__attr_type='U')
        q4 = Q(scraped_obj_attr__attr_type='I')
        return self.scraperelem_set.filter(q1 | q2 | q3 | q4)
    
    def get_mandatory_scrape_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='T')
        q3 = Q(scraped_obj_attr__attr_type='U')
        q4 = Q(scraped_obj_attr__attr_type='I')
        return self.scraperelem_set.filter(q1 | q2 | q3 | q4).filter(mandatory=True)
    
    def get_from_detail_pages_scrape_elems(self):
        return self.scraperelem_set.filter(~Q(request_page_type='MP'))
    
    def __str__(self):
        return self.name + " (" + self.scraped_obj_class.name + ")"
    
    class Meta(object):
        ordering = ['name', 'scraped_obj_class',]


@python_2_unicode_compatible
class RequestPageType(models.Model):
    TYPE_CHOICES = tuple([("MP", "Main Page")] + [("DP{n}".format(n=str(n)), "Detail Page {n}".format(n=str(n))) for n in list(range(1, 26))])
    CONTENT_TYPE_CHOICES = (
        ('H', 'HTML'),
        ('X', 'XML'),
        ('J', 'JSON'),
    )
    REQUEST_TYPE_CHOICES = (
        ('R', 'Request'),
        ('F', 'FormRequest'),
    )
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
    )
    page_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    scraped_obj_attr = models.ForeignKey(ScrapedObjAttr, blank=True, null=True, help_text="Empty for main page, attribute of type DETAIL_PAGE_URL scraped from main page for detail pages.")
    scraper = models.ForeignKey(Scraper)
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPE_CHOICES, default='H', help_text="Data type format for scraped pages of page type (for JSON use JSONPath instead of XPath)")
    render_javascript = models.BooleanField(default=False, help_text="Render Javascript on pages (ScrapyJS/Splash deployment needed, careful: resource intense)")
    request_type = models.CharField(max_length=1, choices=REQUEST_TYPE_CHOICES, default='R', help_text="Normal (typically GET) request (default) or form request (typically POST), using Scrapys corresponding request classes (not used for checker).")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET', help_text="HTTP request via GET or POST.")
    headers = models.TextField(blank=True, help_text='Optional HTTP headers sent with each request, provided as a JSON dict (e.g. {"Referer":"http://referer_url"}, use double quotes!)), can use {main page attribute} and {page} placeholders.')
    body = models.TextField(blank=True, help_text="Optional HTTP message body provided as a unicode string, can use {main page attribute} and {page} placeholders.")
    cookies = models.TextField(blank=True, help_text="Optional cookies as JSON dict (use double quotes!), can use {main page attribute} and {page} placeholders.")
    meta = models.TextField(blank=True, help_text="Optional Scrapy meta attributes as JSON dict (use double quotes!), see Scrapy docs for reference.")
    form_data = models.TextField(blank=True, help_text="Optional HTML form data as JSON dict (use double quotes!), only used with FormRequest request type, can use {main page attribute} and {page} placeholders.")
    dont_filter = models.BooleanField(default=False, help_text="Do not filter duplicate requests, useful for some scenarios with requests falsely marked as being duplicate (e.g. uniform URL + pagination by HTTP header).")
    comments = models.TextField(blank=True)

    def __str__(self):
        ret_str = self.get_page_type_display()
        if self.scraped_obj_attr:
            ret_str += ' (' + str(self.scraped_obj_attr) + ')'
        return ret_str


@python_2_unicode_compatible
class Checker(models.Model):
    CHECKER_TYPE = (
        ('4', '404'),
        ('X', '404_OR_X_PATH'),
    )
    scraped_obj_attr = models.ForeignKey(ScrapedObjAttr, help_text="Attribute of type DETAIL_PAGE_URL, several checkers for same DETAIL_PAGE_URL attribute possible.")
    scraper = models.ForeignKey(Scraper)
    checker_type = models.CharField(max_length=1, choices=CHECKER_TYPE, default='4')
    checker_x_path = models.TextField(blank=True)
    checker_x_path_result = models.TextField(blank=True)
    checker_ref_url = models.URLField(max_length=500, blank=True)
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return  str(self.scraped_obj_attr) + ' > ' + self.get_checker_type_display()
    

@python_2_unicode_compatible
class ScraperElem(models.Model):
    REQUEST_PAGE_TYPE_CHOICES = tuple([("MP", "Main Page")] + [("DP{n}".format(n=str(n)), "Detail Page {n}".format(n=str(n))) for n in list(range(1, 26))])
    help_text = "The different attributes to be scraped, exactly one attribute of type BASE necessary."
    scraped_obj_attr = models.ForeignKey(ScrapedObjAttr, help_text=help_text)
    scraper = models.ForeignKey(Scraper)   
    x_path = models.TextField(blank=True, help_text='XPath or JSONPath expression, leave blank on "static" processor use.')
    reg_exp = models.TextField(blank=True, help_text="Optional filtering by regular expression (e.g. 'Scrape only (.*) the text in between').")
    help_text = "Corresponding Request Page Types created for this scraper."
    request_page_type = models.CharField(max_length=3, choices=REQUEST_PAGE_TYPE_CHOICES, default="MP", help_text=help_text)
    help_text = "Use the default processors (Scrapy TakeFirst, DDS string_strip) for convenience."
    use_default_procs = models.BooleanField(default=True, help_text=help_text)
    help_text = 'Optional comma-separated list of processors used (e.g. "pre_url, post_string").'
    processors = models.TextField(blank=True, help_text=help_text)
    help_text = "Comma-separated aditional context (depending on processor) (e.g. 'pre_url': 'http://append_before.org/', 'post_string': '?append_after=True')."
    proc_ctxt = models.TextField(blank=True, help_text=help_text)
    help_text = "Drop item if attribute could not be scraped."
    mandatory = models.BooleanField(default=True, help_text=help_text)
    
    def __str__(self):
        return '{s} > {soa} Attribute ({rpt})'.format(
            s=str(self.scraper),
            soa=self.scraped_obj_attr.name,
            rpt=self.get_request_page_type_display())
    
    class Meta(object):
        ordering = ['scraped_obj_attr__order',]
    


@python_2_unicode_compatible
class SchedulerRuntime(models.Model):
    TYPE = (
        ('S', 'SCRAPER'),
        ('C', 'CHECKER'),
    )
    runtime_type = models.CharField(max_length=1, choices=TYPE, default='P')
    next_action_time = models.DateTimeField(default=datetime.datetime.now)
    next_action_factor = models.FloatField(blank=True, null=True)
    num_zero_actions = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.id)
    
    class Meta(object):
        ordering = ['next_action_time',]


class LogMarker(models.Model):
    TYPE_CHOICES = (
        ('PE', 'Planned Error'),
        ('DD', 'Dirty Data'),
        ('IM', 'Important'),
        ('IG', 'Ignore'),
        ('MI', 'Miscellaneous'),
        ('CU', 'Custom'),            
    )
    message_contains = models.CharField(max_length=255)
    help_text = "Use the string format from the log messages"
    ref_object = models.CharField(max_length=200, blank=True)
    help_text = 'Choose "Custom" and enter your own type in the next field for a custom type'
    mark_with_type = models.CharField(max_length=2, choices=TYPE_CHOICES, help_text=help_text)
    custom_type = models.CharField(max_length=25, blank=True)
    spider_name = models.CharField(max_length=200, blank=True)
    scraper = models.ForeignKey(Scraper, blank=True, null=True)


class Log(models.Model):
    LEVEL_CHOICES = (
        (50, 'CRITICAL'),
        (40, 'ERROR'),
        (30, 'WARNING'),
        (20, 'INFO'),
        (10, 'DEBUG'),
    )
    message = models.CharField(max_length=255)
    ref_object = models.CharField(max_length=200)
    type = models.CharField(max_length=25, blank=True)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    spider_name = models.CharField(max_length=200)
    scraper = models.ForeignKey(Scraper, blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    
    @staticmethod
    def numeric_level(level):
        numeric_level = 0
        for choice in Log.LEVEL_CHOICES:
            if choice[1] == level:
                numeric_level = choice[0]
        return numeric_level        
    
    class Meta(object):
        ordering = ['-date']
