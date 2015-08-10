# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0006_request_type_and_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='dont_filter',
            field=models.BooleanField(default=False, help_text=b'Do not filter duplicate requests, useful for some scenarios with requests falsely marked as being duplicate (e.g. uniform URL + pagination by HTTP header).'),
        ),
    ]
