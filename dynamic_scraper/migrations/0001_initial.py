# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ScrapedObjClass'
        db.create_table('dynamic_scraper_scrapedobjclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('scraper_scheduler_conf', self.gf('django.db.models.fields.TextField')(default='"MIN_TIME": 15,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 10,\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
            ('checker_scheduler_conf', self.gf('django.db.models.fields.TextField')(default='"MIN_TIME": 1440,\n"MAX_TIME": 10080,\n"INITIAL_NEXT_ACTION_FACTOR": 1,\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\n"FACTOR_CHANGE_FACTOR": 1.3,\n')),
        ))
        db.send_create_signal('dynamic_scraper', ['ScrapedObjClass'])

        # Adding model 'ScrapedObjAttr'
        db.create_table('dynamic_scraper_scrapedobjattr', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('obj_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.ScrapedObjClass'])),
            ('attr_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('dynamic_scraper', ['ScrapedObjAttr'])

        # Adding model 'Scraper'
        db.create_table('dynamic_scraper_scraper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('scraped_obj_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.ScrapedObjClass'])),
            ('max_items', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('use_pagination', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pagination_append_str', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('pagination_on_start', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pagination_range', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('checker_x_path', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('checker_x_path_result', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('checker_x_path_ref_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('dynamic_scraper', ['Scraper'])

        # Adding model 'ScraperElem'
        db.create_table('dynamic_scraper_scraperelem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scraped_obj_attr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.ScrapedObjAttr'])),
            ('scraper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.Scraper'])),
            ('x_path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('reg_exp', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('follow_url', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processors', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('proc_ctxt', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('mandatory', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('dynamic_scraper', ['ScraperElem'])

        # Adding model 'SchedulerRuntime'
        db.create_table('dynamic_scraper_schedulerruntime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('next_action_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('next_action_factor', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('num_zero_actions', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('dynamic_scraper', ['SchedulerRuntime'])

        # Adding model 'ScraperRuntime'
        db.create_table('dynamic_scraper_scraperruntime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('num_criticals', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_critical_msg', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('num_errors', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_error_msg', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('num_warnings', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_warning_msg', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('scheduler_runtime', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.SchedulerRuntime'])),
        ))
        db.send_create_signal('dynamic_scraper', ['ScraperRuntime'])


    def backwards(self, orm):
        
        # Deleting model 'ScrapedObjClass'
        db.delete_table('dynamic_scraper_scrapedobjclass')

        # Deleting model 'ScrapedObjAttr'
        db.delete_table('dynamic_scraper_scrapedobjattr')

        # Deleting model 'Scraper'
        db.delete_table('dynamic_scraper_scraper')

        # Deleting model 'ScraperElem'
        db.delete_table('dynamic_scraper_scraperelem')

        # Deleting model 'SchedulerRuntime'
        db.delete_table('dynamic_scraper_schedulerruntime')

        # Deleting model 'ScraperRuntime'
        db.delete_table('dynamic_scraper_scraperruntime')


    models = {
        'dynamic_scraper.schedulerruntime': {
            'Meta': {'object_name': 'SchedulerRuntime'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_action_factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'next_action_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'num_zero_actions': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'dynamic_scraper.scrapedobjattr': {
            'Meta': {'object_name': 'ScrapedObjAttr'},
            'attr_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'obj_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjClass']"})
        },
        'dynamic_scraper.scrapedobjclass': {
            'Meta': {'object_name': 'ScrapedObjClass'},
            'checker_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 1440,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 1,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scraper_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 15,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 10,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''})
        },
        'dynamic_scraper.scraper': {
            'Meta': {'object_name': 'Scraper'},
            'checker_x_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'checker_x_path_ref_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'checker_x_path_result': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_items': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pagination_append_str': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'pagination_on_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pagination_range': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'scraped_obj_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjClass']"}),
            'use_pagination': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'dynamic_scraper.scraperelem': {
            'Meta': {'object_name': 'ScraperElem'},
            'follow_url': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'proc_ctxt': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'processors': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'reg_exp': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'scraped_obj_attr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.ScrapedObjAttr']"}),
            'scraper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.Scraper']"}),
            'x_path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dynamic_scraper.scraperruntime': {
            'Meta': {'object_name': 'ScraperRuntime'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_critical_msg': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_error_msg': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'last_warning_msg': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'num_criticals': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_errors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_warnings': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scheduler_runtime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.SchedulerRuntime']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'})
        }
    }

    complete_apps = ['dynamic_scraper']
