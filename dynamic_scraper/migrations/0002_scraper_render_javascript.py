# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scraper',
            name='render_javascript',
            field=models.BooleanField(default=False, help_text=b'Render Javascript on pages (ScrapyJS/Splash deployment needed, careful: resource intense)'),
        ),
    ]
