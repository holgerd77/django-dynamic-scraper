# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

def move_from_detail_page_to_request_page_type(apps, schema_editor):
    ScraperElem = apps.get_model("dynamic_scraper", "ScraperElem")
    for se in ScraperElem.objects.all():
        if se.from_detail_page:
            se.request_page_type = 'DP1'
        else:
            se.request_page_type = 'MP'
        se.save()

def create_default_request_page_type_objects(apps, schema_editor):
    Scraper = apps.get_model("dynamic_scraper", "Scraper")
    RequestPageType = apps.get_model("dynamic_scraper", "RequestPageType")
    for scraper in Scraper.objects.all():
        rpt_main = RequestPageType(page_type='MP', scraper=scraper, content_type=scraper.content_type, \
            render_javascript=scraper.render_javascript, request_type=scraper.request_type, method=scraper.method, \
            headers=scraper.headers, body=scraper.body, cookies=scraper.cookies, meta=scraper.meta, \
            form_data=scraper.form_data, dont_filter=scraper.dont_filter)
        rpt_main.save()

        dpu_elems = scraper.scraperelem_set.filter(scraped_obj_attr__attr_type='U')
        if len(dpu_elems) > 0:
            dpu_elem = dpu_elems[0]
            rpt_dp = RequestPageType(page_type='DP1', scraper=scraper, content_type=scraper.detail_page_content_type, \
                scraped_obj_attr=dpu_elem.scraped_obj_attr, render_javascript=scraper.render_javascript, \
                headers=scraper.headers, body=scraper.body, cookies=scraper.cookies, meta=scraper.meta,)
            rpt_dp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0007_dont_filter_attribute'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestPageType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_type', models.CharField(max_length=3, choices=[('MP', 'Main Page'), ('DP1', 'Detail Page 1'), ('DP2', 'Detail Page 2'), ('DP3', 'Detail Page 3'), ('DP4', 'Detail Page 4'), ('DP5', 'Detail Page 5'), ('DP6', 'Detail Page 6'), ('DP7', 'Detail Page 7'), ('DP8', 'Detail Page 8'), ('DP9', 'Detail Page 9'), ('DP10', 'Detail Page 10'), ('DP11', 'Detail Page 11'), ('DP12', 'Detail Page 12'), ('DP13', 'Detail Page 13'), ('DP14', 'Detail Page 14'), ('DP15', 'Detail Page 15'), ('DP16', 'Detail Page 16'), ('DP17', 'Detail Page 17'), ('DP18', 'Detail Page 18'), ('DP19', 'Detail Page 19'), ('DP20', 'Detail Page 20'), ('DP21', 'Detail Page 21'), ('DP22', 'Detail Page 22'), ('DP23', 'Detail Page 23'), ('DP24', 'Detail Page 24'), ('DP25', 'Detail Page 25')])),
                ('content_type', models.CharField(default='H', help_text='Data type format for scraped pages of page type (for JSON use JSONPath instead of XPath)', max_length=1, choices=[('H', 'HTML'), ('X', 'XML'), ('J', 'JSON')])),
                ('render_javascript', models.BooleanField(default=False, help_text='Render Javascript on pages (ScrapyJS/Splash deployment needed, careful: resource intense)')),
                ('request_type', models.CharField(default='R', help_text='Normal (typically GET) request (default) or form request (typically POST), using Scrapys corresponding request classes (not used for checker).', max_length=1, choices=[('R', 'Request'), ('F', 'FormRequest')])),
                ('method', models.CharField(default='GET', help_text='HTTP request via GET or POST.', max_length=10, choices=[('GET', 'GET'), ('POST', 'POST')])),
                ('headers', models.TextField(help_text='Optional HTTP headers sent with each request, provided as a JSON dict (e.g. {"Referer":"http://referer_url"}, use double quotes!)), can use {page} placeholder of pagination.', blank=True)),
                ('body', models.TextField(help_text='Optional HTTP message body provided as a unicode string, can use {page} placeholder of pagination.', blank=True)),
                ('cookies', models.TextField(help_text='Optional cookies as JSON dict (use double quotes!), can use {page} placeholder of pagination.', blank=True)),
                ('meta', models.TextField(help_text='Optional Scrapy meta attributes as JSON dict (use double quotes!), see Scrapy docs for reference.', blank=True)),
                ('form_data', models.TextField(help_text='Optional HTML form data as JSON dict (use double quotes!), only used with FormRequest request type, can use {page} placeholder of pagination.', blank=True)),
                ('dont_filter', models.BooleanField(default=False, help_text='Do not filter duplicate requests, useful for some scenarios with requests falsely marked as being duplicate (e.g. uniform URL + pagination by HTTP header).')),
                ('scraped_obj_attr', models.ForeignKey(blank=True, to='dynamic_scraper.ScrapedObjAttr', help_text='Empty for main page, attribute of type URL scraped from main page for detail pages.', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('scraper', models.ForeignKey(to='dynamic_scraper.Scraper', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='scraperelem',
            name='request_page_type',
            field=models.CharField(default='MP', max_length=3, choices=[('MP', 'Main Page'), ('DP1', 'Detail Page 1'), ('DP2', 'Detail Page 2'), ('DP3', 'Detail Page 3'), ('DP4', 'Detail Page 4'), ('DP5', 'Detail Page 5'), ('DP6', 'Detail Page 6'), ('DP7', 'Detail Page 7'), ('DP8', 'Detail Page 8'), ('DP9', 'Detail Page 9'), ('DP10', 'Detail Page 10'), ('DP11', 'Detail Page 11'), ('DP12', 'Detail Page 12'), ('DP13', 'Detail Page 13'), ('DP14', 'Detail Page 14'), ('DP15', 'Detail Page 15'), ('DP16', 'Detail Page 16'), ('DP17', 'Detail Page 17'), ('DP18', 'Detail Page 18'), ('DP19', 'Detail Page 19'), ('DP20', 'Detail Page 20'), ('DP21', 'Detail Page 21'), ('DP22', 'Detail Page 22'), ('DP23', 'Detail Page 23'), ('DP24', 'Detail Page 24'), ('DP25', 'Detail Page 25')]),
        ),
        migrations.AddField(
            model_name='scraperelem',
            name='save_to_db',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(move_from_detail_page_to_request_page_type),
        migrations.RunPython(create_default_request_page_type_objects),
    ]
