from scrapy import log
from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError

class DjangoWriterPipeline(object):
    
    def process_item(self, item, spider):
        try:
            item['news_website'] = spider.ref_object
            item.save()
            spider.action_successful = True
            spider.log("Item saved.", log.INFO)
                
        except IntegrityError, e:
            spider.log(str(e), log.ERROR)
            raise DropItem("Missing attribute.")
                
        return item