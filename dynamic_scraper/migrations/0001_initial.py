# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
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
                ('level', models.IntegerField(choices=[(50, 'CRITICAL'), (40, 'ERROR'), (30, 'WARNING'), (20, 'INFO'), (10, 'DEBUG')])),
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
                ('mark_with_type', models.CharField(help_text='Choose "Custom" and enter your own type in the next field for a custom type', max_length=2, choices=[('PE', 'Planned Error'), ('DD', 'Dirty Data'), ('IM', 'Important'), ('IG', 'Ignore'), ('MI', 'Miscellaneous'), ('CU', 'Custom')])),
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
                ('runtime_type', models.CharField(default='P', max_length=1, choices=[('S', 'SCRAPER'), ('C', 'CHECKER')])),
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
                ('attr_type', models.CharField(max_length=1, choices=[('S', 'STANDARD'), ('T', 'STANDARD (UPDATE)'), ('B', 'BASE'), ('U', 'DETAIL_PAGE_URL'), ('I', 'IMAGE')])),
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
                ('scraper_scheduler_conf', models.TextField(default='"MIN_TIME": 15,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 10,\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
                ('checker_scheduler_conf', models.TextField(default='"MIN_TIME": 1440,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 1,\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
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
                ('status', models.CharField(default='P', max_length=1, choices=[('A', 'ACTIVE'), ('M', 'MANUAL'), ('P', 'PAUSED'), ('I', 'INACTIVE')])),
                ('content_type', models.CharField(default='H', max_length=1, choices=[('H', 'HTML'), ('X', 'XML')])),
                ('max_items_read', models.IntegerField(help_text='Max number of items to be read (empty: unlimited).', null=True, blank=True)),
                ('max_items_save', models.IntegerField(help_text='Max number of items to be saved (empty: unlimited).', null=True, blank=True)),
                ('pagination_type', models.CharField(default='N', max_length=1, choices=[('N', 'NONE'), ('R', 'RANGE_FUNCT'), ('F', 'FREE_LIST')])),
                ('pagination_on_start', models.BooleanField(default=False)),
                ('pagination_append_str', models.CharField(help_text='Syntax: /somepartofurl/{page}/moreurlstuff.html', max_length=200, blank=True)),
                ('pagination_page_replace', models.TextField(help_text=b"RANGE_FUNCT: uses Python range funct., syntax: [start], stop[, step], FREE_LIST: 'Replace text 1', 'Some other text 2', 'Maybe a number 3', ...", blank=True)),
                ('checker_type', models.CharField(default='N', max_length=1, choices=[('N', 'NONE'), ('4', '404'), ('X', '404_OR_X_PATH')])),
                ('checker_x_path', models.CharField(max_length=200, blank=True)),
                ('checker_x_path_result', models.CharField(max_length=200, blank=True)),
                ('checker_ref_url', models.URLField(max_length=500, blank=True)),
                ('comments', models.TextField(blank=True)),
                ('scraped_obj_class', models.ForeignKey(to='dynamic_scraper.ScrapedObjClass', on_delete=django.db.models.deletion.CASCADE)),
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
                ('scraped_obj_attr', models.ForeignKey(to='dynamic_scraper.ScrapedObjAttr', on_delete=django.db.models.deletion.CASCADE)),
                ('scraper', models.ForeignKey(to='dynamic_scraper.Scraper', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scrapedobjattr',
            name='obj_class',
            field=models.ForeignKey(to='dynamic_scraper.ScrapedObjClass', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logmarker',
            name='scraper',
            field=models.ForeignKey(blank=True, to='dynamic_scraper.Scraper', null=True, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='scraper',
            field=models.ForeignKey(blank=True, to='dynamic_scraper.Scraper', null=True, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
