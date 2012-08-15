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
    comments = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name',]


class ScrapedObjAttr(models.Model):
    ATTR_TYPE_CHOICES = (
        ('S', 'STANDARD'),
        ('T', 'STANDARD (UPDATE)'),
        ('B', 'BASE'),
        ('U', 'DETAIL_PAGE_URL'),
        ('I', 'IMAGE'),
    )
    name = models.CharField(max_length=200)
    obj_class = models.ForeignKey(ScrapedObjClass)
    attr_type = models.CharField(max_length=1, choices=ATTR_TYPE_CHOICES)
    
    def __unicode__(self):
        return self.name + " (" + self.obj_class.__unicode__() + ")"


class Scraper(models.Model):
    STATUS_CHOICES = (
        ('A', 'ACTIVE'),
        ('M', 'MANUAL'),
        ('P', 'PAUSED'),
        ('I', 'INACTIVE'),
    )
    CONTENT_TYPE_CHOICES = (
        ('H', 'HTML'),
        ('X', 'XML'),
    )
    PAGINATION_TYPE = (
        ('N', 'NONE'),
        ('R', 'RANGE_FUNCT'),
        ('F', 'FREE_LIST'),
    )
    CHECKER_TYPE = (
        ('N', 'NONE'),
        ('4', '404'),
        ('X', '404_OR_X_PATH'),
    )
    name = models.CharField(max_length=200)
    scraped_obj_class = models.ForeignKey(ScrapedObjClass)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPE_CHOICES, default='H')
    max_items_read = models.IntegerField(blank=True, null=True, help_text="Max number of items to be read (empty: unlimited).")
    max_items_save = models.IntegerField(blank=True, null=True, help_text="Max number of items to be saved (empty: unlimited).")
    pagination_type = models.CharField(max_length=1, choices=PAGINATION_TYPE, default='N')
    pagination_on_start = models.BooleanField(default=False)
    pagination_append_str = models.CharField(max_length=200, blank=True, help_text="Syntax: /somepartofurl/{page}/moreurlstuff.html")
    pagination_page_replace = models.TextField(blank=True, 
        help_text="RANGE_FUNCT: uses Python range funct., syntax: [start], stop[, step], FREE_LIST: 'Replace text 1', 'Some other text 2', 'Maybe a number 3', ...")
    checker_type = models.CharField(max_length=1, choices=CHECKER_TYPE, default='N')
    checker_x_path = models.CharField(max_length=200, blank=True)
    checker_x_path_result = models.CharField(max_length=200, blank=True)
    checker_ref_url = models.URLField(blank=True)
    comments = models.TextField(blank=True)
    
    def get_base_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='B')
    
    def get_base_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='B')
    
    def get_detail_page_url_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='U')
    
    def get_detail_page_url_elem(self):
        return self.scraperelem_set.get(scraped_obj_attr__attr_type='U')

    def get_standard_elems(self):
        q1 = Q(scraped_obj_attr__attr_type='S')
        q2 = Q(scraped_obj_attr__attr_type='T')
        return self.scraperelem_set.filter(q1 | q2)

    def get_standard_fixed_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='S')

    def get_standard_update_elems(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='T')

    def get_standard_update_elems_from_detail_page(self):
        return self.scraperelem_set.filter(scraped_obj_attr__attr_type='T').filter(from_detail_page=True)
    
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
    
    def get_from_detail_page_scrape_elems(self):
        q1 = Q(from_detail_page=True)
        return self.scraperelem_set.filter(q1)
    
    def __unicode__(self):
        return self.name + " (" + self.scraped_obj_class.name + ")"
    
    class Meta:
        ordering = ['name', 'scraped_obj_class',]


class ScraperElem(models.Model):
    scraped_obj_attr = models.ForeignKey(ScrapedObjAttr)
    scraper = models.ForeignKey(Scraper)   
    x_path = models.CharField(max_length=200)
    reg_exp = models.CharField(max_length=200, blank=True)
    from_detail_page = models.BooleanField()
    processors = models.CharField(max_length=200, blank=True)
    proc_ctxt = models.CharField(max_length=200, blank=True)
    mandatory = models.BooleanField(default=True)


class SchedulerRuntime(models.Model):
    TYPE = (
        ('S', 'SCRAPER'),
        ('C', 'CHECKER'),
    )
    runtime_type = models.CharField(max_length=1, choices=TYPE, default='P')
    next_action_time = models.DateTimeField(default=datetime.datetime.now)
    next_action_factor = models.FloatField(blank=True, null=True)
    num_zero_actions = models.IntegerField(default=0)
    
    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['next_action_time',]


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
