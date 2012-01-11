import datetime
from django.db import models
from django.db.models import Q


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
    
    def __unicode__(self):
        return self.name


class ScrapedObjAttr(models.Model):
    ATTR_TYPE_CHOICES = (
        ('S', 'STANDARD'),
        ('B', 'BASE'),
        ('U', 'FOLLOW_URL'),
        ('I', 'IMAGE'),
    )
    name = models.CharField(max_length=200)
    obj_class = models.ForeignKey(ScrapedObjClass)
    attr_type = models.CharField(max_length=1, choices=ATTR_TYPE_CHOICES)
    
    def __unicode__(self):
        return self.name + " (" + self.obj_class.__unicode__() + ")"


class Scraper(models.Model):
    name = models.CharField(max_length=200)
    scraped_obj_class = models.ForeignKey(ScrapedObjClass)
    max_items = models.IntegerField(blank=True, null=True)
    use_pagination = models.BooleanField(default=False)
    pagination_append_str = models.CharField(max_length=200, blank=True)
    pagination_on_start = models.BooleanField(default=False)
    pagination_range = models.CharField(max_length=200, blank=True)
    checker_x_path = models.CharField(max_length=200, blank=True)
    checker_x_path_result = models.CharField(max_length=200, blank=True)
    checker_x_path_ref_url = models.URLField(blank=True)
    
    def get_base_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='B')
    
    def get_base_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='B')
    
    def get_follow_url_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='U')
    
    def get_follow_url_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='U')

    def get_standard_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='S')

    def get_image_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='I')
    
    def get_image_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='I')
    
    def get_scrape_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='U')
        q3 = Q(scraped_obj_attr__attr_type='I')
        return self.scraperelem_set.filter(q1 | q2 | q3)
    
    def get_mandatory_scrape_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='U')
        q3 = Q(scraped_obj_attr__attr_type='I')
        return self.scraperelem_set.filter(q1 | q2 | q3).filter(mandatory=True)
    
    def __unicode__(self):
        return self.name + " (" + self.scraped_obj_class.name + ")"


class ScraperElem(models.Model):
    scraped_obj_attr = models.ForeignKey(ScrapedObjAttr)
    scraper = models.ForeignKey(Scraper)   
    x_path = models.CharField(max_length=200)
    reg_exp = models.CharField(max_length=200, blank=True)
    follow_url = models.BooleanField()
    processors = models.CharField(max_length=200, blank=True)
    proc_ctxt = models.CharField(max_length=200, blank=True)
    mandatory = models.BooleanField(default=True)


class SchedulerRuntime(models.Model):
    next_action_time = models.DateTimeField(default=datetime.datetime.now)
    next_action_factor = models.FloatField(blank=True, null=True)
    num_zero_actions = models.IntegerField(default=0)
    
    def __unicode__(self):
        return str(self.id)


class ScraperRuntime(models.Model):
    STATUS_CHOICES = (
        ('A', 'ACTIVE'),
        ('P', 'PAUSED'),
        ('I', 'INACTIVE'),
    )
    name = models.CharField(max_length=200)
    scraper = models.ForeignKey(Scraper)
    url = models.URLField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    num_criticals = models.IntegerField(default=0)
    last_critical_msg = models.CharField(max_length=200, blank=True)
    num_errors = models.IntegerField(default=0)
    last_error_msg = models.CharField(max_length=200, blank=True)
    num_warnings = models.IntegerField(default=0)
    last_warning_msg = models.CharField(max_length=200, blank=True)
    scheduler_runtime = models.ForeignKey(SchedulerRuntime)

    def __unicode__(self):
        return self.name + " (" + self.scraper.__unicode__() + ")"