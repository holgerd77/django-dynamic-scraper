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
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
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
            ('status', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('max_items_read', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_items_save', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pagination_type', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('pagination_on_start', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pagination_append_str', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('pagination_page_replace', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('checker_type', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('checker_x_path', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('checker_x_path_result', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('checker_ref_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('dynamic_scraper', ['Scraper'])

        # Adding model 'ScraperElem'
        db.create_table('dynamic_scraper_scraperelem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scraped_obj_attr', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.ScrapedObjAttr'])),
            ('scraper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.Scraper'])),
            ('x_path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('reg_exp', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('from_detail_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processors', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('proc_ctxt', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('mandatory', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('dynamic_scraper', ['ScraperElem'])

        # Adding model 'SchedulerRuntime'
        db.create_table('dynamic_scraper_schedulerruntime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('runtime_type', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('next_action_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('next_action_factor', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('num_zero_actions', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('dynamic_scraper', ['SchedulerRuntime'])

        # Adding model 'Log'
        db.create_table('dynamic_scraper_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ref_object', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('spider_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('scraper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dynamic_scraper.Scraper'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('dynamic_scraper', ['Log'])


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

        # Deleting model 'Log'
        db.delete_table('dynamic_scraper_log')


    models = {
        'dynamic_scraper.log': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ref_object': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scraper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dynamic_scraper.Scraper']", 'null': 'True', 'blank': 'True'}),
            'spider_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dynamic_scraper.schedulerruntime': {
            'Meta': {'object_name': 'SchedulerRuntime'},
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
            'Meta': {'object_name': 'ScrapedObjClass'},
            'checker_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 1440,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 1,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 5,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scraper_scheduler_conf': ('django.db.models.fields.TextField', [], {'default': '\'"MIN_TIME": 15,\\n"MAX_TIME": 10080,\\n"INITIAL_NEXT_ACTION_FACTOR": 10,\\n"ZERO_ACTIONS_FACTOR_CHANGE": 20,\\n"FACTOR_CHANGE_FACTOR": 1.3,\\n\''})
        },
        'dynamic_scraper.scraper': {
            'Meta': {'object_name': 'Scraper'},
            'checker_ref_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'checker_type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'checker_x_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'checker_x_path_result': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
