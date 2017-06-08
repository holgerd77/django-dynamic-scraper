#Stage 2 Update (Python 3)
from __future__ import unicode_literals
from builtins import next
from builtins import str
from builtins import object
import hashlib, logging, ntpath
from dynamic_scraper.models import ScraperElem
from django.utils.encoding import smart_text
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
settings = get_project_settings()



class DjangoImagesPipeline(ImagesPipeline):
    
    def __init__(self, *args, **kwargs):
        super(DjangoImagesPipeline,  self).__init__(*args, **kwargs)
        self.thumbs = settings.get('IMAGES_THUMBS', {})
    
    def get_media_requests(self, item, info):
        try:
            img_elem = info.spider.scraper.get_image_elem()
            if img_elem.scraped_obj_attr.name in item and item[img_elem.scraped_obj_attr.name]:
                if not hasattr(self, 'conf'):
                    self.conf = info.spider.conf
                return Request(item[img_elem.scraped_obj_attr.name])
        except (ScraperElem.DoesNotExist, TypeError):
            pass

    def file_path(self, request, response=None, info=None):
        url = request.url
        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        if self.conf["IMAGES_STORE_FORMAT"] == 'FLAT':
            return '{ig}.jpg'.format(ig=image_guid)
        elif self.conf["IMAGES_STORE_FORMAT"] == 'THUMBS':
            return 'thumbs/{p}/{ig}.jpg'.format(p=next(iter(list(settings.get('IMAGES_THUMBS').keys()))), ig=image_guid)
        else:
            return 'full/{ig}.jpg'.format(ig=image_guid)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        url = request.url
        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        if self.conf["IMAGES_STORE_FORMAT"] == 'FLAT':
            return '{ig}.jpg'.format(ig=image_guid)
        else:
            return 'thumbs/{p}/{ig}.jpg'.format(p=thumb_id, ig=image_guid)

    def item_completed(self, results, item, info):
        try:
            img_elem = info.spider.scraper.get_image_elem()
        except ScraperElem.DoesNotExist:
            return item
        results_list = [x for ok, x in results if ok]
        if len(results_list) > 0:
            item[img_elem.scraped_obj_attr.name] = ntpath.basename(results_list[0]['path'])
        else:
            item[img_elem.scraped_obj_attr.name] = None
        return item

class NoParsingFilter(logging.Filter):
    def filter(self, record=True):
        return False

class ValidationPipeline(object):

    def process_item(self, item, spider):
        
        dds_id = str(item._dds_item_page) + '-' + str(item._dds_item_id)
        if spider.conf['CONSOLE_LOG_LEVEL'] != 'DEBUG':
            logging.getLogger('scrapy.core.scraper').addFilter(NoParsingFilter())
        
        #Process processor placeholders
        for key, value in list(item.items()):
            standard_elems = spider.scraper.get_standard_elems()
            for scraper_elem in standard_elems:
                name = scraper_elem.scraped_obj_attr.name
                placeholder = '{' + name + '}'
                value = smart_text(value)
                if not scraper_elem.scraped_obj_attr.save_to_db:
                    if value and name in spider.non_db_results[id(item)] and \
                       spider.non_db_results[id(item)][name] != None and \
                       placeholder in value:
                        msg = "Applying placeholder {p} on {k}...".format(p=placeholder, k=key)
                        spider.log(msg, logging.DEBUG)
                        spider.log("Value before: " + value, logging.DEBUG)
                        value = value.replace(placeholder, str(spider.non_db_results[id(item)][name]))
                        spider.log("Value after: " + value, logging.DEBUG)
                        item[key] = value
                else:
                    if value and name in item and \
                       item[name] != None and \
                       placeholder in value:
                        msg = "Applying placeholder {p} on {k}...".format(p=placeholder, k=key)
                        spider.log(msg, logging.DEBUG)
                        spider.log("Value before: " + value, logging.DEBUG)
                        value = value.replace(placeholder, str(item[name]))
                        spider.log("Value after: " + value, logging.DEBUG)
                        item[key] = value
        
        idf_elems = spider.scraper.get_id_field_elems()
        is_double = item._is_double
        exist_objects = spider.scraped_obj_class.objects
        
        for idf_elem in idf_elems:
            idf_name = idf_elem.scraped_obj_attr.name
            if idf_name in item and is_double:
                exist_objects = exist_objects.filter(**{idf_name:item[idf_name]})
        
        if is_double:
            mandatory_elems = spider.scraper.get_standard_update_elems()
        else:
            mandatory_elems = spider.scraper.get_mandatory_scrape_elems()
        for elem in mandatory_elems:
            if elem.scraped_obj_attr.save_to_db and (\
                not elem.scraped_obj_attr.name in item or\
                (elem.scraped_obj_attr.name in item and not item[elem.scraped_obj_attr.name])):
                msg = "{cs}Item {id} dropped, mandatory elem {elem} missing!{ce}".format(
                    id=dds_id, elem=elem.scraped_obj_attr.name, cs=spider.bcolors['ERROR'], ce=spider.bcolors['ENDC'])
                spider.log(msg, logging.ERROR)
                raise DropItem()
        
        if spider.conf['MAX_ITEMS_SAVE'] and spider.items_save_count >= spider.conf['MAX_ITEMS_SAVE']:
            spider.log("{cs}Max items save reached ({num}), item {id} not saved or further processed.{ce}".format(
                num=str(spider.conf['MAX_ITEMS_SAVE']), id=dds_id, cs=spider.bcolors["INFO"], ce=spider.bcolors["ENDC"]), logging.INFO)
            raise DropItem()
        
        if not spider.conf['DO_ACTION']:
            spider.log("{cs}Item {id} not saved to Django DB (Test Mode).{ce}".format(
                id=dds_id, cs=spider.bcolors["INFO"], ce=spider.bcolors["ENDC"]), logging.WARNING)
        else:
            if is_double:
                standard_update_elems = spider.scraper.get_standard_update_elems()
                updated_attribute_list = ''
                if len(standard_update_elems) > 0 and len(exist_objects) == 1:
                    exist_object = exist_objects[0]
                    dummy_object = spider.scraped_obj_class()
                    for elem in standard_update_elems:
                        attr_name = elem.scraped_obj_attr.name
                        if attr_name in item and hasattr(exist_object, attr_name):
                            setattr(dummy_object, attr_name, item[attr_name])
                            if str(getattr(dummy_object, attr_name)) != str(getattr(exist_object, attr_name)):
                                setattr(exist_object, attr_name, item[attr_name])
                                if len(updated_attribute_list) > 0:
                                    updated_attribute_list += ', '
                                updated_attribute_list += attr_name
                if len(updated_attribute_list) > 0:
                    exist_object.save()
                    spider.action_successful = True
                    msg = "{cs}Item {id} already in DB, attributes updated: {attr_str}{ce}".format(
                        id=dds_id, attr_str=updated_attribute_list, cs=spider.bcolors["OK"], ce=spider.bcolors["ENDC"])
                    spider.struct_log(msg)
                    raise DropItem()
                else:
                    msg = "{cs}Double item {id}, not saved.{ce}".format(
                        id=dds_id, cs=spider.bcolors["INFO"], ce=spider.bcolors["ENDC"])
                    spider.dds_logger.warning(msg)
                    raise DropItem()
            
            spider.items_save_count += 1

        return item

