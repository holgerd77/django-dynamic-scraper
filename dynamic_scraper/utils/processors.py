import datetime
from scrapy import log


def string_strip(text, loader_context):
    if not (isinstance(text, str) or isinstance(text, unicode)):
        text = str(text)
    chars = loader_context.get('string_strip', ' \n\t\r')
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


def replace(text, loader_context):
    replace = loader_context.get('replace', '')
    return replace


def static(text, loader_context):
    static = loader_context.get('static', '')
    return static


def date(text, loader_context):
    cformat = loader_context.get('date')
    try:
        if text.lower() in ['gestern', 'yesterday',]:
            date = datetime.date.today() - datetime.timedelta(1)
        elif text.lower() in ['heute', 'today',]:
            date = datetime.date.today()
        elif text.lower() in ['morgen', 'tomorrow',]:
            date = datetime.date.today() + datetime.timedelta(1)
        else:
            date = datetime.datetime.strptime(text, cformat)
    except ValueError:
        loader_context.get('spider').log('Date could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
        return None
    return date.strftime('%Y-%m-%d')


def time(text, loader_context):
    cformat = loader_context.get('time')
    try:
        time = datetime.datetime.strptime(text, cformat)
    except ValueError:
        loader_context.get('spider').log('Time could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
        return None
    return time.strftime('%H:%M:%S')


def ts_to_date(ts_str, loader_context):
    try:
        ts_int = int(ts_str)
        return datetime.datetime.fromtimestamp(ts_int).strftime('%Y-%m-%d')
    except ValueError:
        loader_context.get('spider').log('Timestamp could not be parsed ("%s")!' % ts_str, log.ERROR)
        return None


def ts_to_time(ts_str, loader_context):
    try:
        ts_int = int(ts_str)
        return datetime.datetime.fromtimestamp(ts_int).strftime('%H:%M:%S')
    except ValueError:
        loader_context.get('spider').log('Timestamp could not be parsed ("%s")!' % ts_str, log.ERROR)
        return None


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
    #Value completion in special cases
    text_int = None
    try:
        text_int = int(text)
    except ValueError:
        pass
    if(cformat == '%H:%M'):
        if text_int:
            text += ':00'
    if(cformat == '%M'):
        text = _breakdown_time_unit_overlap(text, 60)
        cformat = '%H:%M'
    if(cformat == '%M:%S'):
        if text_int:
            text += ':00'
        text = _breakdown_time_unit_overlap(text, 60)
        cformat = '%H:%M:%S'
    if(cformat == '%S'):
        if text_int:
            if text_int >= 3600:
                hours_str = str(text_int / 3600) + ':'
                secs_under_hour_str = str(text_int % 3600)
                text = hours_str + _breakdown_time_unit_overlap(secs_under_hour_str, 60)
                cformat = '%H:%M:%S'
            else:
                text = _breakdown_time_unit_overlap(text, 60)
                cformat = '%M:%S'
    try:
        duration = datetime.datetime.strptime(text, cformat)
    except ValueError:
        loader_context.get('spider').log('Duration could not be parsed ("%s", Format string: "%s")!' % (text, cformat), log.ERROR)
        return None
    return duration.strftime('%H:%M:%S')
