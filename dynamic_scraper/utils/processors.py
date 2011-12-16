from datetime import datetime
from scrapy import log

def string_strip(text, loader_context):
    chars = loader_context.get('string_strip', ' \n\t')
    return text.strip(chars)
    
def pre_string(text, loader_context):
    pre_str = loader_context.get('pre_string', '')
    
    return pre_str  + text

def post_string(text, loader_context):
    post_str = loader_context.get('post_string', '')
    
    return text + post_str

def pre_url(text, loader_context):
    pre_url = loader_context.get('pre_url', '')

    if(pre_url[0:7] == 'http://' and text[0:7] == 'http://'):
        return text
    
    if(pre_url[-1:] == '/' and text[0:1] == '/'):
        pre_url = pre_url[:-1]
    
    return pre_url + text

def date(text, loader_context):
    cformat = loader_context.get('date')
    try:
        date = datetime.strptime(text, cformat)
    except ValueError:
        log.msg(loader_context.get('pre_log_msg') + "Date could not be parsed!", log.ERROR)
        return None
    return date.strftime('%Y-%m-%d')

def time(text, loader_context):
    cformat = loader_context.get('time')
    try:
        time = datetime.strptime(text, cformat)
    except ValueError:
        log.msg(loader_context.get('pre_log_msg') + "Time could not be parsed!", log.ERROR)
        return None
    return time.strftime('%H:%M')

def _breakdown_time_unit_overlap(time_str, limit):
    time_list = time_str.split(':')
    first = int(time_list[0])
    if first >= limit:
        time_list[0] = str(first % limit)
        time_list.insert(0, str(first // limit))
    else:
        if(len(time_list[0]) == 1):
            time_list[0] = '0' + time_list[0]
        time_list.insert(0, '00')
    time_str = ':'.join(time_list)
    return time_str

def duration(text, loader_context):
    cformat = loader_context.get('duration')
    if(cformat == '%M'):
        text = _breakdown_time_unit_overlap(text, 60)
        cformat = '%H:%M'
    if(cformat == '%M:%S'):
        text = _breakdown_time_unit_overlap(text, 60)
        cformat = '%H:%M:%S'
    if(cformat == '%S'):
        text = _breakdown_time_unit_overlap(text, 60)
        cformat = '%M:%S'
    try:
        duration = datetime.strptime(text, cformat)
    except ValueError:
        log.msg(loader_context.get('pre_log_msg') + "Duration could not be parsed!", log.ERROR)
        return None
    return duration.strftime('%H:%M:%S')
