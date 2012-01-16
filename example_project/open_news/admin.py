from django.contrib import admin
from open_news.models import NewsWebsite, Article

class NewsWebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'news_website', 'url_',)

    def url_(self, instance):
        return '<a href="%s" target="_blank">%s</a>' % (instance.url, instance.url)
    url_.allow_tags = True

admin.site.register(NewsWebsite, NewsWebsiteAdmin)
admin.site.register(Article, ArticleAdmin)