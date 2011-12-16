from django.db import models
from dynamic_scraper.models import Scraper, ScraperRuntime, SchedulerRuntime
from scrapy.contrib_exp.djangoitem import DjangoItem


class NewsWebsite(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    scraper = models.ForeignKey(Scraper)
    scraper_runtime = models.ForeignKey(ScraperRuntime)
    
    def __unicode__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    news_website = models.ForeignKey(NewsWebsite) 
    description = models.TextField(blank=True)
    url = models.URLField()
    thumbnail = models.CharField(max_length=200)
    checker_runtime = models.ForeignKey(SchedulerRuntime)
    
    def __unicode__(self):
        return self.title


class ArticleItem(DjangoItem):
    django_model = Article