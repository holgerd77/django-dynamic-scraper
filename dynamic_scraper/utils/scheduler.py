import ast, datetime
from django.core.exceptions import ImproperlyConfigured

class Scheduler():
    
    
    def __init__(self, conf_dict_str):
        self.conf = self._parse_conf_dict_str(conf_dict_str)
        mandatory_vars = [
            'MIN_TIME',
            'MAX_TIME',
            'INITIAL_NEXT_ACTION_FACTOR',
            'ZERO_ACTIONS_FACTOR_CHANGE',
            'FACTOR_CHANGE_FACTOR',
        ]
        for var in mandatory_vars:
            if var not in self.conf:
                raise ImproperlyConfigured("Missing config value for scheduler: %s" % var)
        
    def _parse_conf_dict_str(self, conf_dict_str):
        try:
            conf = conf_dict_str.strip(', ')
            conf = conf.replace('\r\n','')
            conf = ast.literal_eval("{" + conf + "}")
        except SyntaxError:
            raise ImproperlyConfigured("Wrong context definition format: %s" % conf_dict_str)
        return conf
    
    
    def calc_next_action_time(self, action_successful, next_action_factor, num_zero_actions):
        if not next_action_factor:
            next_action_factor = self.conf['INITIAL_NEXT_ACTION_FACTOR']
        if action_successful:
            num_zero_actions = 0
            next_action_factor = next_action_factor / self.conf['FACTOR_CHANGE_FACTOR']
        else:
            num_zero_actions += 1
            if(num_zero_actions >= self.conf['ZERO_ACTIONS_FACTOR_CHANGE']):
                num_zero_actions = 0
                next_action_factor = next_action_factor * self.conf['FACTOR_CHANGE_FACTOR']
        
        time_delta = round(self.conf['MIN_TIME'] * next_action_factor, 0)
        next_action_factor = round(next_action_factor, 3)
        time_delta = max(time_delta, self.conf['MIN_TIME'])
        time_delta = min(time_delta, self.conf['MAX_TIME'])
        time_delta = datetime.timedelta(minutes=int(time_delta))    
        result = (time_delta, next_action_factor, num_zero_actions)
        
        return result
        
