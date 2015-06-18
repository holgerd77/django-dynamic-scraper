"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime, os, time
from django.test import TestCase
from dynamic_scraper.utils import processors

class ProcessorsTest(TestCase):
    
    def test_string_strip(self):
        result_str = processors.string_strip("  This text makes no sense!     ", {})
        self.assertEqual(result_str, 'This text makes no sense!')
    
        result_str = processors.string_strip("..This text makes no sense!-----", {'string_strip': '.-'})
        self.assertEqual(result_str, 'This text makes no sense!')
    
    
    def test_pre_string(self):
        result_str = processors.pre_string("text", {'pre_string': 'before_'})
        self.assertEqual(result_str, 'before_text')
    
    
    def test_post_string(self):
        result_str = processors.post_string("text", {'post_string': '_after'})
        self.assertEqual(result_str, 'text_after')
    
    
    def test_pre_url(self):
        result_str = processors.pre_url("/path/document.html", {'pre_url': 'http://example.com'})
        self.assertEqual(result_str, 'http://example.com/path/document.html')
        
        result_str = processors.pre_url("http://example.com/path/document.html", {'pre_url': 'http://example.com'})
        self.assertEqual(result_str, 'http://example.com/path/document.html')
        
        # Eliminating double slashes
        result_str = processors.pre_url("/path/document.html", {'pre_url': 'http://example.com/'})
        self.assertEqual(result_str, 'http://example.com/path/document.html')
    
    
    def test_replace(self):
        result_str = processors.replace("Random text", {'replace': 'Something totally different'})
        self.assertEqual(result_str, 'Something totally different')
    
    
    def test_date(self):
        result_str = processors.date('2011-12-15', {'date': '%Y-%m-%d'})
        self.assertEqual(result_str, '2011-12-15')
        
        result_str = processors.date('15.12.2011', {'date': '%d.%m.%Y'})
        self.assertEqual(result_str, '2011-12-15')
        
        result_str = processors.date('15 Dec 2011', {'date': '%d %b %Y'})
        self.assertEqual(result_str, '2011-12-15')
        
        result_str = processors.date('gestern', {'date': '%d %b %Y'})
        self.assertEqual(result_str, (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d'))
        
        result_str = processors.date('yesterday', {'date': '%d %b %Y'})
        self.assertEqual(result_str, (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d'))
        
        result_str = processors.date('heute', {'date': '%d %b %Y'})
        self.assertEqual(result_str, datetime.date.today().strftime('%Y-%m-%d'))
        
        result_str = processors.date('today', {'date': '%d %b %Y'})
        self.assertEqual(result_str, datetime.date.today().strftime('%Y-%m-%d'))
    
        result_str = processors.date('morgen', {'date': '%d %b %Y'})
        self.assertEqual(result_str, (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))
        
        result_str = processors.date('tomorrow', {'date': '%d %b %Y'})
        self.assertEqual(result_str, (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'))
        
    
    def test_time(self):
        result_str = processors.time('22:15', {'time': '%H:%M'})
        self.assertEqual(result_str, '22:15:00')
        
        result_str = processors.time('22 Uhr 15', {'time': '%H Uhr %M'})
        self.assertEqual(result_str, '22:15:00')
    

    def test_ts_to_date(self):
        os.environ['TZ'] = 'Europe/Berlin'
        time.tzset()
        result_str = processors.ts_to_date('1434560700', {})
        self.assertEqual(result_str, '2015-06-17')


    def test_ts_to_time(self):
        os.environ['TZ'] = 'Europe/Berlin'
        time.tzset()
        result_str = processors.ts_to_time('1434560700', {})
        self.assertEqual(result_str, '19:05:00')

    
    def test_duration(self):
        result_str = processors.duration('01:25', {'duration': '%H:%M'})
        self.assertEqual(result_str, '01:25:00')

        result_str = processors.duration('1:25', {'duration': '%H:%M'})
        self.assertEqual(result_str, '01:25:00')
        
        result_str = processors.duration('1', {'duration': '%H:%M'})
        self.assertEqual(result_str, '01:00:00')

        result_str = processors.duration('1:25:37', {'duration': '%H:%M:%S'})
        self.assertEqual(result_str, '01:25:37')
   
        result_str = processors.duration('4:35', {'duration': '%M:%S'})
        self.assertEqual(result_str, '00:04:35')
        
        result_str = processors.duration('77:35', {'duration': '%M:%S'})
        self.assertEqual(result_str, '01:17:35')
        
        result_str = processors.duration('1', {'duration': '%M:%S'})
        self.assertEqual(result_str, '00:01:00')
        
        result_str = processors.duration('47', {'duration': '%M'})
        self.assertEqual(result_str, '00:47:00')
        
        result_str = processors.duration('77', {'duration': '%M'})
        self.assertEqual(result_str, '01:17:00')
        
        result_str = processors.duration('62', {'duration': '%S'})
        self.assertEqual(result_str, '00:01:02')
        
        result_str = processors.duration('3600', {'duration': '%S'})
        self.assertEqual(result_str, '01:00:00')
        
        result_str = processors.duration('3605', {'duration': '%S'})
        self.assertEqual(result_str, '01:00:05')
        
        result_str = processors.duration('5127', {'duration': '%S'})
        self.assertEqual(result_str, '01:25:27')
        
        result_str = processors.duration('2 hours 17 minutes 15 seconds', {'duration': '%H hours %M minutes %S seconds'})
        self.assertEqual(result_str, '02:17:15')

