from datetime import date
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from dynamic_scraper.models import *


class ScrapedObjAttrFormSet(BaseInlineFormSet):
    
    def clean(self):
        super(ScrapedObjAttrFormSet, self).clean()

        cnt_type_b = 0
        cnt_type_u = 0
        cnt_type_i = 0
        cnt_id = 0
        cnt_wrong_id_type = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if 'DELETE' in data and data['DELETE']:
                continue
            if not 'attr_type' in data or not 'id_field' in data:
                continue
            at = data['attr_type']
            if at == 'B':
                cnt_type_b += 1
            if at == 'U':
                cnt_type_u += 1
            if at == 'I':
                cnt_type_i += 1
            id_field = data['id_field']
            if id_field:
                cnt_id += 1
                if (at != 'S' and at != 'U'):
                    cnt_wrong_id_type += 1

        if cnt_type_b == 0:
            raise ValidationError("For the scraped object class definition one object attribute of type BASE is required!")
        if cnt_type_b > 1:
            raise ValidationError("Only one object attribute of type BASE allowed!")
        if cnt_type_u > 25:
            raise ValidationError("Maximum number of 25 detail page URLs supported!")
        if cnt_type_i > 1:
            raise ValidationError("Currently only one image per object supported!")

        if cnt_wrong_id_type > 0:
            raise ValidationError("Only STANDARD or DETAIL_PAGE_URL attributes can be defined as ID fields!")



class ScrapedObjAttrInline(admin.TabularInline):
    model = ScrapedObjAttr
    formset = ScrapedObjAttrFormSet
    extra = 3


class ScrapedObjClassAdmin(admin.ModelAdmin):
    inlines = [
        ScrapedObjAttrInline
    ]


class RequestPageTypeFormSet(BaseInlineFormSet):
    
    def clean(self):
        super(RequestPageTypeFormSet, self).clean()

        cnt_rpts = 0
        cnt_rpts_mp = 0
        cnt_rpts_dp = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            if 'DELETE' in data and data['DELETE']:
                continue
            if not 'page_type' in data:
                continue
            cnt_rpts += 1

            pt = data['page_type']
            if pt == 'MP':
                cnt_rpts_mp += 1
            else:
                cnt_rpts_dp += 1

        if cnt_rpts_mp == 0:
            raise ValidationError("For every request page type used for scraper elems definition a RequestPageType object with a corresponding page type has to be added!")
        if cnt_rpts_mp > 1:
            raise ValidationError("Only one RequestPageType object for main page requests allowed!")

class RequestPageTypeInline(admin.StackedInline):
    model = RequestPageType
    formset = RequestPageTypeFormSet
    extra = 0

class CheckerInline(admin.StackedInline):
    model = Checker
    extra = 0

class ScraperElemInline(admin.TabularInline):
    model = ScraperElem
    extra = 3

    
class ScraperAdmin(admin.ModelAdmin):
    class Media:
        js = ("js/admin_custom.js",)
    list_display = ('id', 'name', 'scraped_obj_class', 'status', 'max_items_read', 'max_items_save', \
        'pagination_type', 'rpts', 'checkers',)
    list_display_links = ('name',)
    list_editable = ('status',)
    list_filter = ('scraped_obj_class', 'status', 'pagination_type',)
    search_fields = ['name']
    inlines = [
        RequestPageTypeInline,
        CheckerInline,
        ScraperElemInline
    ]
    fieldsets = (
        (None, {
            'fields': ('name', 'scraped_obj_class', 'status', \
                'max_items_read', 'max_items_save')
        }),
        (None, {
            'fields': ('pagination_type',)
        }),
        ('Pagination options', {
            'classes': ('collapse',),
            'fields': ('pagination_on_start', 'pagination_append_str', 'pagination_page_replace')
        }),
        (None, {
            'fields': ('comments',)
        }),
    )
    
    def rpts(self, obj):
        return unicode(obj.requestpagetype_set.count())
    
    def checkers(self, obj):
        cnt = obj.checker_set.count()
        if cnt > 0:
            return unicode(cnt)
        else:
            return ""
    
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