# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0008_new_request_page_types_construct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scraper',
            name='body',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='cookies',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='detail_page_content_type',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='dont_filter',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='form_data',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='headers',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='meta',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='method',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='render_javascript',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='request_type',
        ),
        migrations.RemoveField(
            model_name='scraperelem',
            name='from_detail_page',
        ),
    ]
