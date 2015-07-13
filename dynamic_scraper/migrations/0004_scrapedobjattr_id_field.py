# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_id_to_detail_page_url_scraped_obj_attributes(apps, schema_editor):
    ScrapedObjAttr = apps.get_model("dynamic_scraper", "ScrapedObjAttr")
    for soa in ScrapedObjAttr.objects.all():
        if soa.attr_type == 'U':
            soa.id_field = True
            soa.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0003_auto_20150610_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedobjattr',
            name='id_field',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(add_id_to_detail_page_url_scraped_obj_attributes)
    ]
