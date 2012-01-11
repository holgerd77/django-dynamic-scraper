from django.contrib import admin
from open_news.models import NewsWebsite, Article

class NewsWebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'news_website', 'show_url',)

    def show_url(self, instance):
        return '<a href="%s" target="_blank">%s</a>' % (instance.url, instance.url)
    show_url.allow_tags = True

admin.site.register(NewsWebsite, NewsWebsiteAdmin)
admin.site.register(Article, ArticleAdmin)