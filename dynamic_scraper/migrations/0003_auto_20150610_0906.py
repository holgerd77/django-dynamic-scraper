# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0002_scraper_render_javascript'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='detail_page_content_type',
            field=models.CharField(default='H', help_text='Data type format for detail pages and checker (for JSON use JSONPath instead of XPath)', max_length=1, choices=[('H', 'HTML'), ('X', 'XML'), ('J', 'JSON')]),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='content_type',
            field=models.CharField(default='H', help_text='Data type format for scraped main pages (for JSON use JSONPath instead of XPath)', max_length=1, choices=[('H', 'HTML'), ('X', 'XML'), ('J', 'JSON')]),
        ),
    ]
