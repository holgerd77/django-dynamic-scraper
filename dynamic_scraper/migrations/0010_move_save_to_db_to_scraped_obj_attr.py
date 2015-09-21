# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0009_removed_legacy_request_page_type_scraper_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scraperelem',
            name='save_to_db',
        ),
        migrations.AddField(
            model_name='scrapedobjattr',
            name='save_to_db',
            field=models.BooleanField(default=True),
        ),
    ]
