# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0005_new_dict_params_for_scraper'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='body',
            field=models.TextField(help_text='Optional HTTP message body provided as a unicode string, can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='method',
            field=models.CharField(default='GET', help_text='HTTP request via GET or POST.', max_length=10, choices=[('GET', 'GET'), ('POST', 'POST')]),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='cookies',
            field=models.TextField(help_text='Optional cookies as JSON dict (use double quotes!), can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='form_data',
            field=models.TextField(help_text='Optional HTML form data as JSON dict (use double quotes!), only used with FormRequest request type, can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='headers',
            field=models.TextField(help_text='Optional HTTP headers sent with each request, provided as a JSON dict (e.g. {"Referer":"http://referer_url"}, use double quotes!)), can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='meta',
            field=models.TextField(help_text='Optional Scrapy meta attributes as JSON dict (use double quotes!), see Scrapy docs for reference.', blank=True),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='request_type',
            field=models.CharField(default='R', help_text='Normal (typically GET) request (default) or form request (typically POST), using Scrapys corresponding request classes (not used for checker).', max_length=1, choices=[('R', 'Request'), ('F', 'FormRequest')]),
        ),
    ]
