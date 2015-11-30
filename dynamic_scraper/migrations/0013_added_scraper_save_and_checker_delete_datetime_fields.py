# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0012_removed_legacy_checker_scraper_attributes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scrapedobjclass',
            options={'ordering': ['name'], 'verbose_name': 'Scraped object class', 'verbose_name_plural': 'Scraped object classes'},
        ),
        migrations.AddField(
            model_name='scraper',
            name='last_checker_delete',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='last_scraper_save',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
