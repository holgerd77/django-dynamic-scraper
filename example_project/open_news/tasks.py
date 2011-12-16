from celery.decorators import task

from dynamic_scraper.utils.task_utils import TaskUtils
from open_news.models import NewsWebsite, Article

@task()
def run_spiders():
    t = TaskUtils()
    t.run_spiders(NewsWebsite, 'scraper_runtime', 'article_spider')
    
@task()
def run_checkers():
    t = TaskUtils()
    t.run_checkers(Article, 'checker_runtime', 'article_checker')