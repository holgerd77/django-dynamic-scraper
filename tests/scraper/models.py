from django.db import models
from dynamic_scraper.models import Scraper, ScraperRuntime, SchedulerRuntime
from scrapy.contrib_exp.djangoitem import DjangoItem


class EventWebsite(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    scraper = models.ForeignKey(Scraper)
    scraper_runtime = models.ForeignKey(ScraperRuntime)
    
    def __unicode__(self):
        return self.name + " (" + str(self.id) + ")"


class Event(models.Model):
    title = models.CharField(max_length=200)
    event_website = models.ForeignKey(EventWebsite) 
    description = models.TextField(blank=True)
    url = models.URLField()
    checker_runtime = models.ForeignKey(SchedulerRuntime)
    
    def __unicode__(self):
        return self.title + " (" + str(self.id) + ")"


class EventItem(DjangoItem):
    django_model = Event