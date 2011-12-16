import datetime
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from dynamic_scraper.utils.scheduler import Scheduler


class SchedulerTest(TestCase):
    
    
    def test_config_wrong_def(self):
        conf_dict_str = '\
"MIN_TIME" ---- 15,\n\
"MAX_TIME": 10080,\n\
"INITIAL_NEXT_ACTION_FACTOR": 10,\n\
"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n\
"FACTOR_CHANGE_FACTOR": 1.3,\n'
        self.assertRaises(ImproperlyConfigured, Scheduler, conf_dict_str)


    def test_config_missing_value_max_time(self):
        conf_dict_str = '\
"MIN_TIME": 15,\n\
"INITIAL_NEXT_ACTION_FACTOR": 10,\n\
"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n\
"FACTOR_CHANGE_FACTOR": 1.3,\n'
        self.assertRaises(ImproperlyConfigured, Scheduler, conf_dict_str)
    
    
    def test_calc_next_action_time(self):
        conf_dict_str = '\
"MIN_TIME": 15,\n\
"MAX_TIME": 10080,\n\
"INITIAL_NEXT_ACTION_FACTOR": 10,\n\
"ZERO_ACTIONS_FACTOR_CHANGE": 20,\n\
"FACTOR_CHANGE_FACTOR": 1.3,\n'
        sched = Scheduler(conf_dict_str)
        
        # Successful action, not-initialized next action factor
        result = sched.calc_next_action_time(True, None, 0)
        self.assertEqual(result, (datetime.timedelta(minutes=115), 7.692, 0))
        
        # Successful action
        result = sched.calc_next_action_time(True, 13, 9)
        self.assertEqual(result, (datetime.timedelta(minutes=150), 10, 0))
        
        # Successful action, new time delta under min time
        result = sched.calc_next_action_time(True, 1, 9)
        self.assertEqual(result, (datetime.timedelta(minutes=15), 0.769, 0))
        
        # Successful action, not-initialized next action factor
        result = sched.calc_next_action_time(False, None, 0)
        self.assertEqual(result, (datetime.timedelta(minutes=150), 10, 1))
        
        # Unsuccessful action, no new action factor
        result = sched.calc_next_action_time(False, 10, 18)
        self.assertEqual(result, (datetime.timedelta(minutes=150), 10, 19))
        
        # Unsuccessful action, new action factor
        result = sched.calc_next_action_time(False, 10, 19)
        self.assertEqual(result, (datetime.timedelta(minutes=195), 13, 0))