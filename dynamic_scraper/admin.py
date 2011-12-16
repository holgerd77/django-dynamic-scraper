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
    inlines = [
        ScraperElemInline
    ]

admin.site.register(ScrapedObjClass, ScrapedObjClassAdmin)
admin.site.register(Scraper, ScraperAdmin)
admin.site.register(ScraperRuntime)
admin.site.register(SchedulerRuntime)