#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from builtins import str
from django.db import models
from dynamic_scraper.models import Scraper, SchedulerRuntime
from scrapy_djangoitem import DjangoItem


@python_2_unicode_compatible
class EventWebsite(models.Model):
    name = models.CharField(max_length=200)
    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)
    url = models.URLField()
    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name + " (" + str(self.id) + ")"


@python_2_unicode_compatible
class Event(models.Model):
    title = models.CharField(max_length=200)
    event_website = models.ForeignKey(EventWebsite) 
    description = models.TextField(blank=True)
    description2 = models.TextField(blank=True)
    url = models.URLField(blank=True)
    url2 = models.URLField(blank=True)
    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.title + " (" + str(self.id) + ")"

    def detailed(self):
        str  = "title: {t}\n".format(t=self.title)
        str += "event_website:"
        return str


class EventItem(DjangoItem):
    django_model = Event