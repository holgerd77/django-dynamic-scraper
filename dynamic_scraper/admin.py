from datetime import date
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
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
    list_editable = ('status',)
    list_filter = ('scraped_obj_class', 'status', 'content_type', 'pagination_type', 'checker_type',)
    search_fields = ['name']
    inlines = [
        ScraperElemInline
    ]
    actions = ['clone_scrapers',]
    
    def clone_scrapers(self, request, queryset):
        for scraper in queryset:
            scraper_elems = scraper.scraperelem_set.all()
            scraper.pk = None
            scraper.name = scraper.name + " (COPY)"
            scraper.status = 'P'
            scraper.save()
            for se in scraper_elems:
                se.pk = None
                se.scraper = scraper
                se.save()
        
        rows_updated = queryset.count()
        if rows_updated == 1:
            message_bit = "1 scraper was"
        else:
            message_bit = "%s scrapers were" % rows_updated
        self.message_user(request, "%s successfully cloned." % message_bit)
    
    clone_scrapers.short_description = "Clone selected scrapers"


class SchedulerRuntimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'runtime_type', 'next_action_time', 'next_action_factor', 'num_zero_actions',)
    list_filter = ('runtime_type',)
    search_fields = ['id']


class LogMarkerAdmin(admin.ModelAdmin):
    list_display = ('message_contains', 'ref_object', 'mark_with_type', 'custom_type', 'spider_name', 'scraper',)
    list_filter = ('mark_with_type', 'custom_type', 'spider_name', 'scraper',)
    search_fields = ('message_contains',)


class LogDateFilter(SimpleListFilter):    
    title = _('date')
    parameter_name = 'date'
    
    def lookups(self, request, model_admin):
        return (
            ('today', _('today')),
            ('yesterday', _('yesterday')),
            ('last_hour', _('last hour')),
            ('last_6_hours', _('last 6 hours')),
            ('last_24_hours', _('last 24 hours')),
            ('last_week', _('last_week')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'today':
            comp_date = datetime.datetime.today()
            return queryset.filter(
                date__year=comp_date.year,
                date__month=comp_date.month,
                date__day=comp_date.day,
            )
        if self.value() == 'yesterday':
            comp_date = datetime.datetime.today() - datetime.timedelta(1)
            return queryset.filter(
                date__year=comp_date.year,
                date__month=comp_date.month,
                date__day=comp_date.day,
            )
        if self.value() == 'last_hour':
            comp_date = datetime.datetime.now() - datetime.timedelta(0, 0, 0, 0, 0, 1)
            return queryset.filter(
                date__gt=comp_date
            )
        if self.value() == 'last_6_hours':
            comp_date = datetime.datetime.now() - datetime.timedelta(0, 0, 0, 0, 0, 6)
            return queryset.filter(
                date__gt=comp_date
            )
        if self.value() == 'last_24_hours':
            comp_date = datetime.datetime.now() - datetime.timedelta(1)
            return queryset.filter(
                date__gt=comp_date
            )
        if self.value() == 'last_week':
            comp_date = datetime.datetime.now() - datetime.timedelta(7)
            return queryset.filter(
                date__gt=comp_date
            )

class LogAdmin(admin.ModelAdmin):
    list_display = ('message', 'ref_object', 'type', 'level', 'spider_name', 'scraper_', 'date_',)
    list_filter = (LogDateFilter, 'type', 'level', 'spider_name', 'scraper',)
    search_fields = ['ref_object',]

    def scraper_(self, instance):
        return instance.scraper.name
    
    def date_(self, instance):
        return instance.date.strftime('%Y-%m-%d %H:%M')


admin.site.register(ScrapedObjClass, ScrapedObjClassAdmin)
admin.site.register(Scraper, ScraperAdmin)
admin.site.register(SchedulerRuntime, SchedulerRuntimeAdmin)
admin.site.register(LogMarker, LogMarkerAdmin)
admin.site.register(Log, LogAdmin)