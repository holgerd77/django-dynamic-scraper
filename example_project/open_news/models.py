from django.db import models
from scrapy.contrib_exp.djangoitem import DjangoItem
from dynamic_scraper.models import ScraperRuntime, SchedulerRuntime


class NewsWebsite(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    scraper_runtime = models.ForeignKey(ScraperRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        scraper_runtime = self.scraper_runtime
        super(NewsWebsite, self).delete(*args, **kwargs)
        scraper_runtime.delete()


class Article(models.Model):
    title = models.CharField(max_length=200)
    news_website = models.ForeignKey(NewsWebsite) 
    description = models.TextField(blank=True)
    url = models.URLField()
    thumbnail = models.CharField(max_length=200)
    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.title

    def delete(self, *args, **kwargs):
        checker_runtime = self.checker_runtime
        super(Article, self).delete(*args, **kwargs)
        checker_runtime.delete()


class ArticleItem(DjangoItem):
    django_model = Article
