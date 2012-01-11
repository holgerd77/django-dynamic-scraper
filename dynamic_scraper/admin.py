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
    list_display = ('name', 'scraped_obj_class', 'max_items', 'use_pagination',)
    list_filter = ('scraped_obj_class',)
    search_fields = ['name']
    inlines = [
        ScraperElemInline
    ]

class ScraperRuntimeAdmin(admin.ModelAdmin):
    list_display = ('name', 'scraper', 'show_url', 'status', 'scheduler_runtime',)
    list_filter = ('scraper', 'status',)
    search_fields = ['name']
    
    def show_url(self, instance):
        return '<a href="%s" target="_blank">%s</a>' % (instance.url, instance.url)
    show_url.allow_tags = True

class SchedulerRuntimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'next_action_time', 'next_action_factor', 'num_zero_actions',)
    search_fields = ['id']

admin.site.register(ScrapedObjClass, ScrapedObjClassAdmin)
admin.site.register(Scraper, ScraperAdmin)
admin.site.register(ScraperRuntime, ScraperRuntimeAdmin)
admin.site.register(SchedulerRuntime, SchedulerRuntimeAdmin)