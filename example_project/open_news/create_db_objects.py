
import sys
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path = sys.path + [os.path.join(PROJECT_ROOT, '../..'), os.path.join(PROJECT_ROOT, '..')]

from django.core.management import setup_environ
import example_project.settings
setup_environ(example_project.settings)


from dynamic_scraper.models import *
from open_news.models import NewsWebsite, Article


sc = ScrapedObjClass(name='Article')
sc.save()
soa_base = ScrapedObjAttr(name=u'base', attr_type='B', obj_class=sc)
soa_base.save()
soa_desc = ScrapedObjAttr(name=u'description', attr_type='S', obj_class=sc)
soa_desc.save()
soa_title = ScrapedObjAttr(name=u'title', attr_type='S', obj_class=sc)
soa_title.save()
soa_url = ScrapedObjAttr(name=u'url', attr_type='U', obj_class=sc)
soa_url.save()
soa_thumb = ScrapedObjAttr(name=u'thumbnail', attr_type='I', obj_class=sc)
soa_thumb.save()

scraper = Scraper(name=u'Wikinews Scraper', scraped_obj_class=sc)
scraper.save()

se_base = ScraperElem(scraped_obj_attr=soa_base, scraper=scraper, 
x_path=u'//td[@class="l_box"]', follow_url=False)
se_base.save()
se_title = ScraperElem(scraped_obj_attr=soa_title, scraper=scraper, 
    x_path=u'//h1[@id="firstHeading"]/text()', follow_url=True)
se_title.save()
se_desc = ScraperElem(scraped_obj_attr=soa_desc, scraper=scraper, 
    x_path=u'p/span[@class="l_summary"]/text()', follow_url=False)
se_desc.save()
se_url = ScraperElem(scraped_obj_attr=soa_url, scraper=scraper, 
    x_path=u'span[@class="l_title"]/a/@href', follow_url=False, processors='pre_url',
    proc_ctxt="'pre_url': 'http://en.wikinews.org'")
se_url.save()
se_thumb = ScraperElem(scraped_obj_attr=soa_thumb, scraper=scraper, 
    x_path=u'div[@class="l_image"]/a/img/@src', follow_url=False, processors='pre_url',
    proc_ctxt="'pre_url': 'http:'")
se_thumb.save()

sched_rt = SchedulerRuntime()
sched_rt.save()

scraper_rt = ScraperRuntime(name=u'Article Scraper Runtime', scheduler_runtime=sched_rt)
scraper_rt.save()

news_website = NewsWebsite(pk=1, name=u'Wikinews', url=u'http://en.wikinews.org/wiki/Main_Page',
    scraper=scraper, scraper_runtime=scraper_rt)
news_website.save()