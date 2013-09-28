# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Scraper.checker_ref_url'
        db.alter_column('dynamic_scraper_scraper', 'checker_ref_url', self.gf('django.db.models.fields.URLField')(max_length=500))

    def backwards(self, orm):

        # Changing field 'Scraper.checker_ref_url'
        db.alter_column('dynamic_scraper_scraper', 'checker_ref_url', self.gf('django.db.models.fields.URLField')(max_length=200))

    models = {
        'dynamic_scraper.log': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ref_object': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scraper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.Scraper']", 'null': 'True', 'blank': 'True'}),
            'spider_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'})
        },
        'dynamic_scraper.logmarker': {
            'Meta': {'object_name': 'LogMarker'},
            'custom_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark_with_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'message_contains': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ref_object': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'scraper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.Scraper']", 'null': 'True', 'blank': 'True'}),
            'spider_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'dynamic_scraper.schedulerruntime': {
            'Meta': {'ordering': "['next_action_time']", 'object_name': 'SchedulerRuntime'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_action_factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'next_action_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'num_zero_actions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'runtime_type': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'})
        },
        'dynamic_scraper.scrapedobjattr': {
            'Meta': {'object_name': 'ScrapedObjAttr'},
            'attr_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'obj_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjClass']"})
        },
        'dynamic_scraper.scrapedobjclass': {
            'Meta': {'ordering': "['name']", 'object_name': 'ScrapedObjClass'},
            'checker_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 1440,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 1,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scraper_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 15,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 10,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''})
        },
        'dynamic_scraper.scraper': {
            'Meta': {'ordering': "['name', 'scraped_obj_class']", 'object_name': 'Scraper'},
            'checker_ref_url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'blank': 'True'}),
            'checker_type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'checker_x_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'checker_x_path_result': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'H'", 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_items_read': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_items_save': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pagination_append_str': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'pagination_on_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pagination_page_replace': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pagination_type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'scraped_obj_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjClass']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'})
        },
        'dynamic_scraper.scraperelem': {
            'Meta': {'object_name': 'ScraperElem'},
            'from_detail_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'proc_ctxt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'processors': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'reg_exp': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'scraped_obj_attr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjAttr']"}),
            'scraper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.Scraper']"}),
            'x_path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['dynamic_scraper']