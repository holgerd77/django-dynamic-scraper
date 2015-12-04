# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0014_added_scraper_save_and_checker_delete_alert_period_fields_for_scraper'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='next_last_checker_delete_alert',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='Next time the last checker delete will be alerted, normally set on management cmd run.'),
        ),
        migrations.AddField(
            model_name='scraper',
            name='next_last_scraper_save_alert',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='Next time the last scraper save will be alerted, normally set on management cmd run.'),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='last_checker_delete_alert_period',
            field=models.CharField(help_text="Optional, used for scraper monitoring with 'check_last_checker_deletes' management cmd,         syntax: [HOURS]h or [DAYS]d or [WEEKS]w (e.g. '6h', '5d', '2w')", max_length=5, blank=True),
        ),
        migrations.AlterField(
            model_name='scraper',
            name='last_scraper_save_alert_period',
            field=models.CharField(help_text="Optional, used for scraper monitoring with 'check_last_scraper_saves' management cmd,         syntax: [HOURS]h or [DAYS]d or [WEEKS]w (e.g. '6h', '5d', '2w')", max_length=5, blank=True),
        ),
    ]
