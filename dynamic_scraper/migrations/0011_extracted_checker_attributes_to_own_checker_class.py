# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_default_checker_objects(apps, schema_editor):
    Scraper = apps.get_model("dynamic_scraper", "Scraper")
    Checker = apps.get_model("dynamic_scraper", "Checker")
    for s in Scraper.objects.all():
        url_elem = None
        url_id_elems = s.scraperelem_set.filter(scraped_obj_attr__attr_type='U', scraped_obj_attr__id_field=True)
        url_elems = s.scraperelem_set.filter(scraped_obj_attr__attr_type='U')
        if url_id_elems.count() > 0:
            url_elem = url_id_elems[0]
        elif url_elems.count() > 0:
            url_elem = url_elems[0]
        if s.checker_type != 'N' and url_elem:
            c = Checker(scraped_obj_attr=url_elem.scraped_obj_attr, scraper=s, checker_type=s.checker_type, \
                checker_x_path=s.checker_x_path, checker_x_path_result=s.checker_x_path_result, \
                checker_ref_url=s.checker_ref_url)
            c.save()
    

class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_scraper', '0010_move_save_to_db_to_scraped_obj_attr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('checker_type', models.CharField(default=b'4', max_length=1, choices=[(b'4', b'404'), (b'X', b'404_OR_X_PATH')])),
                ('checker_x_path', models.CharField(max_length=200, blank=True)),
                ('checker_x_path_result', models.CharField(max_length=200, blank=True)),
                ('checker_ref_url', models.URLField(max_length=500, blank=True)),
                ('comments', models.TextField(blank=True)),
                ('scraped_obj_attr', models.ForeignKey(help_text=b'Attribute of type DETAIL_PAGE_URL, several checkers for same DETAIL_PAGE_URL attribute possible.', to='dynamic_scraper.ScrapedObjAttr')),
                ('scraper', models.ForeignKey(to='dynamic_scraper.Scraper')),
            ],
        ),
        migrations.AddField(
            model_name='requestpagetype',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='requestpagetype',
            name='scraped_obj_attr',
            field=models.ForeignKey(blank=True, to='dynamic_scraper.ScrapedObjAttr', help_text=b'Empty for main page, attribute of type DETAIL_PAGE_URL scraped from main page for detail pages.', null=True),
        ),
        migrations.RunPython(create_default_checker_objects),
    ]
