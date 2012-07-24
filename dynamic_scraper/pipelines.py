import hashlib
from dynamic_scraper.models import ScraperElem
from scrapy import log
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request


'''
Getting PIL to work on Mac OS under virtualenv:
Download combo installer or libjpeg installer from http://ethan.tira-thompson.com/Mac_OS_X_Ports.html
pip install -I pil --no-install
Uncomment JPEG_ROOT and change to JPEG_ROOT = libinclude("/usr/local") in setup.py
pip install -I pil --no-download

from:
http://ubuntuforums.org/showthread.php?p=10811107
http://stackoverflow.com/questions/4435016/install-pil-on-virtualenv-with-libjpeg
'''
class DjangoImagesPipeline(ImagesPipeline):
    
    def get_media_requests(self, item, info):
        try:
            img_elem = info.spider.scraper.get_image_elem()
            if img_elem.scraped_obj_attr.name in item and item[img_elem.scraped_obj_attr.name]:
                return Request(item[img_elem.scraped_obj_attr.name])
        except (ScraperElem.DoesNotExist, TypeError):
            pass

    def image_key(self, url):
        image_guid = hashlib.sha1(url).hexdigest()
        return '%s.jpg' % (image_guid)

    def thumb_key(self, url, thumb_id):
        image_guid = hashlib.sha1(url).hexdigest()
        return '%s.jpg' % (image_guid)

    def item_completed(self, results, item, info):
        try:
            img_elem = info.spider.scraper.get_image_elem()
        except ScraperElem.DoesNotExist:
            return item
        
        results_list = [x for ok, x in results if ok]
        if len(results_list) > 0:
            item[img_elem.scraped_obj_attr.name] = results_list[0]['path']
        else:
            item[img_elem.scraped_obj_attr.name] = None
        return item


class ValidationPipeline(object):

    def process_item(self, item, spider):
        
        url_elem = spider.scraper.get_detail_page_url_elem()
        url_name = url_elem.scraped_obj_attr.name
        if url_name in item and item[url_name][0:6] == 'DOUBLE':
            mandatory_elems = spider.scraper.get_standard_update_elems()
        else:
            mandatory_elems = spider.scraper.get_mandatory_scrape_elems()
        for elem in mandatory_elems:
            if not elem.scraped_obj_attr.name in item or\
                (elem.scraped_obj_attr.name in item and not item[elem.scraped_obj_attr.name]):
                spider.log("Mandatory elem " + elem.scraped_obj_attr.name + " missing!", log.ERROR)
                raise DropItem()
        
        if spider.conf['MAX_ITEMS_SAVE'] and spider.items_save_count >= spider.conf['MAX_ITEMS_SAVE']:
            spider.log("Max items save reached, item not saved.", log.INFO)
            raise DropItem()
        
        if not spider.conf['DO_ACTION']:
            spider.log("TESTMODE: Item not saved.", log.INFO)
            raise DropItem()
        
        url_elem = spider.scraper.get_detail_page_url_elem()
        url_name = url_elem.scraped_obj_attr.name
        if url_name in item and item[url_name][0:6] == 'DOUBLE':
            item[url_name] = item[url_name][6:]
            standard_update_elems = spider.scraper.get_standard_update_elems()
            updated_attribute_list = ''
            if len(standard_update_elems) > 0:
                exist_objects = spider.scraped_obj_class.objects.filter(url=item[url_name])
                if len(exist_objects) == 1:
                    exist_object = exist_objects[0]
                    dummy_object = spider.scraped_obj_class()
                    for elem in standard_update_elems:
                        attr_name = elem.scraped_obj_attr.name
                        if attr_name in item and hasattr(exist_object, attr_name):
                            setattr(dummy_object, attr_name, item[attr_name])
                            if unicode(getattr(dummy_object, attr_name)) != unicode(getattr(exist_object, attr_name)):
                                setattr(exist_object, attr_name, item[attr_name])
                                if len(updated_attribute_list) > 0:
                                    updated_attribute_list += ', '
                                updated_attribute_list += attr_name
            if len(updated_attribute_list) > 0:
                exist_object.save()
                raise DropItem("Item already in DB, attributes updated: " + updated_attribute_list)
            else:
                raise DropItem("Double item.")
        
        spider.items_save_count += 1

        return item

