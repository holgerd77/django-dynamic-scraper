# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0011_extracted_checker_attributes_to_own_checker_class'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scraper',
            name='checker_ref_url',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='checker_type',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='checker_x_path',
        ),
        migrations.RemoveField(
            model_name='scraper',
            name='checker_x_path_result',
        ),
    ]
