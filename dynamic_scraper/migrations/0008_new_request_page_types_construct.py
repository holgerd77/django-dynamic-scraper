# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
                ('page_type', models.CharField(max_length=3, choices=[(b'MP', b'Main Page'), (b'DP1', b'Detail Page 1'), (b'DP2', b'Detail Page 2'), (b'DP3', b'Detail Page 3'), (b'DP4', b'Detail Page 4'), (b'DP5', b'Detail Page 5'), (b'DP6', b'Detail Page 6'), (b'DP7', b'Detail Page 7'), (b'DP8', b'Detail Page 8'), (b'DP9', b'Detail Page 9'), (b'DP10', b'Detail Page 10'), (b'DP11', b'Detail Page 11'), (b'DP12', b'Detail Page 12'), (b'DP13', b'Detail Page 13'), (b'DP14', b'Detail Page 14'), (b'DP15', b'Detail Page 15'), (b'DP16', b'Detail Page 16'), (b'DP17', b'Detail Page 17'), (b'DP18', b'Detail Page 18'), (b'DP19', b'Detail Page 19'), (b'DP20', b'Detail Page 20'), (b'DP21', b'Detail Page 21'), (b'DP22', b'Detail Page 22'), (b'DP23', b'Detail Page 23'), (b'DP24', b'Detail Page 24'), (b'DP25', b'Detail Page 25')])),
                ('content_type', models.CharField(default=b'H', help_text=b'Data type format for scraped pages of page type (for JSON use JSONPath instead of XPath)', max_length=1, choices=[(b'H', b'HTML'), (b'X', b'XML'), (b'J', b'JSON')])),
                ('render_javascript', models.BooleanField(default=False, help_text=b'Render Javascript on pages (ScrapyJS/Splash deployment needed, careful: resource intense)')),
                ('request_type', models.CharField(default=b'R', help_text=b'Normal (typically GET) request (default) or form request (typically POST), using Scrapys corresponding request classes (not used for checker).', max_length=1, choices=[(b'R', b'Request'), (b'F', b'FormRequest')])),
                ('method', models.CharField(default=b'GET', help_text=b'HTTP request via GET or POST.', max_length=10, choices=[(b'GET', b'GET'), (b'POST', b'POST')])),
                ('headers', models.TextField(help_text=b'Optional HTTP headers sent with each request, provided as a JSON dict (e.g. {"Referer":"http://referer_url"}, use double quotes!)), can use {page} placeholder of pagination.', blank=True)),
                ('body', models.TextField(help_text=b'Optional HTTP message body provided as a unicode string, can use {page} placeholder of pagination.', blank=True)),
                ('cookies', models.TextField(help_text=b'Optional cookies as JSON dict (use double quotes!), can use {page} placeholder of pagination.', blank=True)),
                ('meta', models.TextField(help_text=b'Optional Scrapy meta attributes as JSON dict (use double quotes!), see Scrapy docs for reference.', blank=True)),
                ('form_data', models.TextField(help_text=b'Optional HTML form data as JSON dict (use double quotes!), only used with FormRequest request type, can use {page} placeholder of pagination.', blank=True)),
                ('dont_filter', models.BooleanField(default=False, help_text=b'Do not filter duplicate requests, useful for some scenarios with requests falsely marked as being duplicate (e.g. uniform URL + pagination by HTTP header).')),
                ('scraped_obj_attr', models.ForeignKey(blank=True, to='dynamic_scraper.ScrapedObjAttr', help_text=b'Empty for main page, attribute of type URL scraped from main page for detail pages.', null=True)),
                ('scraper', models.ForeignKey(to='dynamic_scraper.Scraper')),
            ],
        ),
        migrations.AddField(
            model_name='scraperelem',
            name='request_page_type',
            field=models.CharField(default=b'MP', max_length=3, choices=[(b'MP', b'Main Page'), (b'DP1', b'Detail Page 1'), (b'DP2', b'Detail Page 2'), (b'DP3', b'Detail Page 3'), (b'DP4', b'Detail Page 4'), (b'DP5', b'Detail Page 5'), (b'DP6', b'Detail Page 6'), (b'DP7', b'Detail Page 7'), (b'DP8', b'Detail Page 8'), (b'DP9', b'Detail Page 9'), (b'DP10', b'Detail Page 10'), (b'DP11', b'Detail Page 11'), (b'DP12', b'Detail Page 12'), (b'DP13', b'Detail Page 13'), (b'DP14', b'Detail Page 14'), (b'DP15', b'Detail Page 15'), (b'DP16', b'Detail Page 16'), (b'DP17', b'Detail Page 17'), (b'DP18', b'Detail Page 18'), (b'DP19', b'Detail Page 19'), (b'DP20', b'Detail Page 20'), (b'DP21', b'Detail Page 21'), (b'DP22', b'Detail Page 22'), (b'DP23', b'Detail Page 23'), (b'DP24', b'Detail Page 24'), (b'DP25', b'Detail Page 25')]),
        ),
        migrations.AddField(
            model_name='scraperelem',
            name='save_to_db',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(move_from_detail_page_to_request_page_type),
        migrations.RunPython(create_default_request_page_type_objects),
    ]
