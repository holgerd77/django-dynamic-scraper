from dynamic_scraper.spiders.django_checker import DjangoChecker
from open_news.models import Article


class ArticleChecker(DjangoChecker):
    
    name = 'article_checker'
    
    def __init__(self, *args, **kwargs):
        self._set_ref_object(Article, **kwargs)
        self.scraper = self.ref_object.news_website.scraper
        #self.scrape_url = self.ref_object.url
        self.scheduler_runtime = self.ref_object.checker_runtime
        super(ArticleChecker, self).__init__(self, *args, **kwargs)