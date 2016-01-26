# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0016_optional_xpath_fields_text_type_for_x_path_reg_exp_processor_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scrapedobjattr',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='scraperelem',
            options={'ordering': ['scraped_obj_attr__order']},
        ),
        migrations.AddField(
            model_name='scrapedobjattr',
            name='order',
            field=models.IntegerField(default=100),
        ),
    ]
