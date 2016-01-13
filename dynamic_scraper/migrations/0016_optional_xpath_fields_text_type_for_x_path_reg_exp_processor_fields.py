# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0015_added_datetime_fields_for_last_scraper_save_and_checker_delete_alert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checker',
            name='checker_x_path',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='checker',
            name='checker_x_path_result',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='scraperelem',
            name='proc_ctxt',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='scraperelem',
            name='processors',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='scraperelem',
            name='reg_exp',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='scraperelem',
            name='x_path',
            field=models.TextField(blank=True),
        ),
    ]
