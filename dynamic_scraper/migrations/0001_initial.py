# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=255)),
                ('ref_object', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=25, blank=True)),
                ('level', models.IntegerField(choices=[(50, b'CRITICAL'), (40, b'ERROR'), (30, b'WARNING'), (20, b'INFO'), (10, b'DEBUG')])),
                ('spider_name', models.CharField(max_length=200)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_contains', models.CharField(max_length=255)),
                ('ref_object', models.CharField(max_length=200, blank=True)),
                ('mark_with_type', models.CharField(help_text=b'Choose "Custom" and enter your own type in the next field for a custom type', max_length=2, choices=[(b'PE', b'Planned Error'), (b'DD', b'Dirty Data'), (b'IM', b'Important'), (b'IG', b'Ignore'), (b'MI', b'Miscellaneous'), (b'CU', b'Custom')])),
                ('custom_type', models.CharField(max_length=25, blank=True)),
                ('spider_name', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchedulerRuntime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('runtime_type', models.CharField(default=b'P', max_length=1, choices=[(b'S', b'SCRAPER'), (b'C', b'CHECKER')])),
                ('next_action_time', models.DateTimeField(default=datetime.datetime.now)),
                ('next_action_factor', models.FloatField(null=True, blank=True)),
                ('num_zero_actions', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['next_action_time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScrapedObjAttr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('attr_type', models.CharField(max_length=1, choices=[(b'S', b'STANDARD'), (b'T', b'STANDARD (UPDATE)'), (b'B', b'BASE'), (b'U', b'DETAIL_PAGE_URL'), (b'I', b'IMAGE')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScrapedObjClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('scraper_scheduler_conf', models.TextField(default=b'"MIN_TIME": 15,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 10,\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
                ('checker_scheduler_conf', models.TextField(default=b'"MIN_TIME": 1440,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 1,\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scraper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'A', b'ACTIVE'), (b'M', b'MANUAL'), (b'P', b'PAUSED'), (b'I', b'INACTIVE')])),
                ('content_type', models.CharField(default=b'H', max_length=1, choices=[(b'H', b'HTML'), (b'X', b'XML')])),
                ('max_items_read', models.IntegerField(help_text=b'Max number of items to be read (empty: unlimited).', null=True, blank=True)),
                ('max_items_save', models.IntegerField(help_text=b'Max number of items to be saved (empty: unlimited).', null=True, blank=True)),
                ('pagination_type', models.CharField(default=b'N', max_length=1, choices=[(b'N', b'NONE'), (b'R', b'RANGE_FUNCT'), (b'F', b'FREE_LIST')])),
                ('pagination_on_start', models.BooleanField(default=False)),
                ('pagination_append_str', models.CharField(help_text=b'Syntax: /somepartofurl/{page}/moreurlstuff.html', max_length=200, blank=True)),
                ('pagination_page_replace', models.TextField(help_text=b"RANGE_FUNCT: uses Python range funct., syntax: [start], stop[, step], FREE_LIST: 'Replace text 1', 'Some other text 2', 'Maybe a number 3', ...", blank=True)),
                ('checker_type', models.CharField(default=b'N', max_length=1, choices=[(b'N', b'NONE'), (b'4', b'404'), (b'X', b'404_OR_X_PATH')])),
                ('checker_x_path', models.CharField(max_length=200, blank=True)),
                ('checker_x_path_result', models.CharField(max_length=200, blank=True)),
                ('checker_ref_url', models.URLField(max_length=500, blank=True)),
                ('comments', models.TextField(blank=True)),
                ('scraped_obj_class', models.ForeignKey(to='dynamic_scraper.ScrapedObjClass')),
            ],
            options={
                'ordering': ['name', 'scraped_obj_class'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScraperElem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x_path', models.CharField(max_length=200)),
                ('reg_exp', models.CharField(max_length=200, blank=True)),
                ('from_detail_page', models.BooleanField(default=False)),
                ('processors', models.CharField(max_length=200, blank=True)),
                ('proc_ctxt', models.CharField(max_length=200, blank=True)),
                ('mandatory', models.BooleanField(default=True)),
                ('scraped_obj_attr', models.ForeignKey(to='dynamic_scraper.ScrapedObjAttr')),
                ('scraper', models.ForeignKey(to='dynamic_scraper.Scraper')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scrapedobjattr',
            name='obj_class',
            field=models.ForeignKey(to='dynamic_scraper.ScrapedObjClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logmarker',
            name='scraper',
            field=models.ForeignKey(blank=True, to='dynamic_scraper.Scraper', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='scraper',
            field=models.ForeignKey(blank=True, to='dynamic_scraper.Scraper', null=True),
            preserve_default=True,
        ),
    ]
