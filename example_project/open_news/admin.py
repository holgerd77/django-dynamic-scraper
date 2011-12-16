from django.contrib import admin
from open_news.models import NewsWebsite, Article

class NewsWebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__',)

admin.site.register(NewsWebsite, NewsWebsiteAdmin)
admin.site.register(Article, ArticleAdmin)