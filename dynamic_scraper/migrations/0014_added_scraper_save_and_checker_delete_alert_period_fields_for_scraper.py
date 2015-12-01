# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0013_added_scraper_save_and_checker_delete_datetime_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='last_checker_delete_alert_period',
            field=models.CharField(help_text="Optional, used for scraper monitoring with 'check_last_checker_deletes' management cmd,         syntax: <hours>h or <days>d or <weeks>w (e.g. '6h', '5d', '2w')", max_length=5, blank=True),
        ),
        migrations.AddField(
            model_name='scraper',
            name='last_scraper_save_alert_period',
            field=models.CharField(help_text="Optional, used for scraper monitoring with 'check_last_scraper_saves' management cmd,         syntax: <hours>h or <days>d or <weeks>w (e.g. '6h', '5d', '2w')", max_length=5, blank=True),
        ),
    ]
