from __future__ import unicode_literals
from builtins import str
from builtins import object
import logging
from django.db.utils import IntegrityError
from scrapy.exceptions import DropItem
from dynamic_scraper.models import SchedulerRuntime

class DjangoWriterPipeline(object):
    
    def process_item(self, item, spider):
        if spider.conf['DO_ACTION']:
            try:
                item['news_website'] = spider.ref_object
                
                checker_rt = SchedulerRuntime(runtime_type='C')
                checker_rt.save()
                item['checker_runtime'] = checker_rt
                
                item.save()
                spider.action_successful = True
                dds_id_str = str(item._dds_item_page) + '-' + str(item._dds_item_id)
                spider.struct_log("{cs}Item {id} saved to Django DB.{ce}".format(
                    id=dds_id_str,
                    cs=spider.bcolors['OK'],
                    ce=spider.bcolors['ENDC']))
                    
            except IntegrityError as e:
                spider.log(str(e), logging.ERROR)
                raise DropItem("Missing attribute.")
                
        return item