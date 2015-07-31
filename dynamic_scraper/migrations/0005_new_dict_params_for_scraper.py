# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0004_scrapedobjattr_id_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='cookies',
            field=models.TextField(help_text=b'Optional cookies as JSON dict, can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='form_data',
            field=models.TextField(help_text=b'Optional HTML form data as JSON dict, only used with FormRequest request type, can use {page} placeholder of pagination.', blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='headers',
            field=models.TextField(help_text=b"Optional HTTP headers sent with each request - provided as a JSON dict (e.g. {'Referer':'http://referer_url'})).", blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='meta',
            field=models.TextField(help_text=b'Optional Scrapy meta attributes as JSON dict, see Scrapy docs for reference.', blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='request_type',
            field=models.CharField(default=b'R', help_text=b'Normal GET request (default) or form request via POST, using Scrapys corresponding request classes (not used for checker).', max_length=1, choices=[(b'R', b'Request (GET)'), (b'F', b'FormRequest (POST)')]),
        ),
    ]
