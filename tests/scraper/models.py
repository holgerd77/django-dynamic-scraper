from django.db import models
from dynamic_scraper.models import Scraper, SchedulerRuntime
from scrapy.contrib.djangoitem import DjangoItem


class EventWebsite(models.Model):
    name = models.CharField(max_length=200)
    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)
    url = models.URLField()
    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.name + " (" + str(self.id) + ")"


class Event(models.Model):
    title = models.CharField(max_length=200)
    event_website = models.ForeignKey(EventWebsite) 
    description = models.TextField(blank=True)
    description2 = models.TextField(blank=True)
    url = models.URLField(blank=True)
    url2 = models.URLField(blank=True)
    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.title + " (" + str(self.id) + ")"

    def detailed(self):
        str  = "title: %s\n" % self.title
        str += "event_website:"
        return str


class EventItem(DjangoItem):
    django_model = Event