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
    PAGINATION_TYPE = (
        ('N', 'NONE'),
        ('R', 'RANGE_FUNCT'),
        ('F', 'FREE_LIST'),
    )
    name = models.CharField(max_length=200)
    scraped_obj_class = models.ForeignKey(ScrapedObjClass)
    max_items_read = models.IntegerField(blank=True, null=True, help_text="Max number of items to be read (empty: unlimited).")
    max_items_save = models.IntegerField(blank=True, null=True, help_text="Max number of items to be saved (empty: unlimited).")
    pagination_type = models.CharField(max_length=1, choices=PAGINATION_TYPE, default='N')
    pagination_on_start = models.BooleanField(default=False)
    pagination_append_str = models.CharField(max_length=200, blank=True, help_text="Syntax: /somepartofurl/{page}/moreurlstuff.html")
    pagination_page_replace = models.TextField(blank=True, 
        help_text="RANGE_FUNCT: uses Python range funct., syntax: [start], stop[, step], FREE_LIST: 'Replace text 1', 'Some other text 2', 'Maybe a number 3', ...")
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
    
    def get_scrape_elems_with_follow_url(self):
        q1 = Q(follow_url=True)
        return self.scraperelem_set.filter(q1)
    
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
    scheduler_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    def delete(self, *args, **kwargs):
        scheduler_runtime = self.scheduler_runtime
        super(ScraperRuntime, self).delete(*args, **kwargs)
        scheduler_runtime.delete()

    def __unicode__(self):
        return self.name + " (" + self.scraper.__unicode__() + ")"


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
    level = models.IntegerField(choices=LEVEL_CHOICES)
    spider_name = models.CharField(max_length=200)
    scraper_runtime = models.ForeignKey(ScraperRuntime, blank=True, null=True)
    scraper = models.ForeignKey(Scraper, blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    
    @staticmethod
    def numeric_level(level):
        numeric_level = 0
        for choice in Log.LEVEL_CHOICES:
            if choice[1] == level:
                numeric_level = choice[0]
        return numeric_level        
    
    class Meta:
        ordering = ['-date']
