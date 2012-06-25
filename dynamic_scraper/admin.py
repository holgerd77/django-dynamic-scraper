from django.contrib import admin
from dynamic_scraper.models import *

class ScrapedObjAttrInline(admin.TabularInline):
    model = ScrapedObjAttr
    extra = 3

class ScrapedObjClassAdmin(admin.ModelAdmin):
    inlines = [
        ScrapedObjAttrInline
    ]
    
class ScraperElemInline(admin.TabularInline):
    model = ScraperElem
    extra = 3
    
class ScraperAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'scraped_obj_class', 'status', 'content_type', 'max_items_read', 'max_items_save', 'pagination_type', 'checker_type',)
    list_display_links = ('name',)
    list_filter = ('scraped_obj_class', 'status', 'content_type', 'pagination_type', 'checker_type',)
    search_fields = ['name']
    inlines = [
        ScraperElemInline
    ]

class SchedulerRuntimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'runtime_type', 'next_action_time', 'next_action_factor', 'num_zero_actions',)
    list_filter = ('runtime_type',)
    search_fields = ['id']

class LogAdmin(admin.ModelAdmin):
    list_display = ('message', 'ref_object', 'level', 'spider_name', 'scraper_', 'date_',)
    list_filter = ('level', 'spider_name', 'scraper',)
    search_fields = ['ref_object',]

    def scraper_(self, instance):
        return instance.scraper.name
    
    def date_(self, instance):
        return instance.date.strftime('%Y-%m-%d %H:%M')


admin.site.register(ScrapedObjClass, ScrapedObjClassAdmin)
admin.site.register(Scraper, ScraperAdmin)
admin.site.register(SchedulerRuntime, SchedulerRuntimeAdmin)
admin.site.register(Log, LogAdmin)