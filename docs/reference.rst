=========
Reference
=========

.. _settings:

Settings
========

For the configuration of Django Dynamic Scraper you can use all the basic `settings from 
Scrapy <http://doc.scrapy.org/en/latest/topics/settings.html>`_, though some settings may
not be useful to change in the context of DDS. In addition DDS defines some extra settings
with the prefix ``DSCRAPER``. You can also place these settings in the Scrapy ``settings.py``
configuration file. At the moment this is the only way to define DDS settings and you can't 
change DDS settings via command line parameters.


DSCRAPER_IMAGES_STORE_FORMAT
----------------------------
Default: ``FLAT``

Store format for images (see :ref:`scraping_images` for more info).

====== ================================================================================
FLAT   Storing only either original or one thumbnail image, no sub folders
ALL    Storing original (in ``full/``) and thumbnail images (e.g. in ``thumbs/small/``)
THUMBS Storing only the thumbnail images (e.g. in ``thumbs/small/``)
====== ================================================================================

.. _setting_dscraper_custom_processors:

DSCRAPER_CUSTOM_PROCESSORS
--------------------------
Default: ``[]``

List with Python paths to custom processor modules, e.g.::

	DSCRAPER_CUSTOM_PROCESSORS = [
	    'scraper_module.scraper.processors',
	    'scraper_module.scraper.more_processors',
	    //...
	]

DSCRAPER_SPLASH_ARGS
--------------------
Default: ``{ 'wait': 0.5 }``

Customize ``Splash`` args when ``ScrapyJS/Splash`` is used for Javascript rendering.

DSCRAPER_LOG_ENABLED
--------------------
Default: ``True``

Enable/disable the DDS logging.

.. note::
   The ``DSCRAPER_LOG_*`` settings customize the behaviour DDS logs for
	 post analysis of your scraper runs in the DB (see :ref:`logging` for more info).
	 Console output log is controlled by the regularly ``Scrapy`` log settings/options.
	 

DSCRAPER_LOG_LEVEL
------------------
Default: ``ERROR``

Set the log level for DDS logging. Possible values are CRITICAL, ERROR, WARNING, INFO and DEBUG.

DSCRAPER_LOG_LIMIT
------------------
Default: ``250``

The number of log entries in the Django database table.

DSCRAPER_MAX_SPIDER_RUNS_PER_TASK
---------------------------------
Default: ``10``

Maximum number of spider runs executed per task run.

DSCRAPER_MAX_CHECKER_RUNS_PER_TASK
----------------------------------
Default: ``25``

Maximum number of checker runs executed per task run.

Django Model Reference
======================

TODO

.. _scraped_obj_class:

ScrapedObjClass
---------------

TODO

.. _scraped_obj_attr:

ScrapedObjAttr
--------------

TODO

.. _scraper:

Scraper
-------

``status``
^^^^^^^^^^
		
Status of the scraper, influencing in which context the scraper is executed.
		
======== ===========================================================================
ACTIVE   Scraper can be run manually and is included on scheduled task execution
MANUAL   Scraper can only be run manually and is ignored on scheduled task execution
PAUSE    Scraper is not executed, use for short pausing
INACTIVE Scraper is not executed, use for longer interruption of scraper use
======== ===========================================================================

.. _scraper_elem:

ScraperElem
-----------

TODO


.. _scheduler_runtime:

SchedulerRuntime
----------------

TODO


API Reference
=============

TODO

.. _django_spider:

DjangoSpider
------------

By default ``DjangoSpider`` uses ``scrapy.loaders.processors.TakeFirst`` loader. It means that it will take first value from group of found elements. 

You can change this behaviour following way: 

	from scrapy.loader.processors import Join
	
	class MySpider(DjangoSpider):
	    def _get_processors(self, *args, **kwargs):
	        procs = super(MySpider, self)._get_processors(*args, **kwargs)
	        procs = (Join(','), ) + procs[1:]
	        return procs

.. _django_checker:

DjangoChecker
-------------

TODO

.. _processors:

Processors
==========

General Functionality
---------------------

.. _attribute_placeholders:

Attribute Placeholders
^^^^^^^^^^^^^^^^^^^^^^
Processors can use placeholders referencing other scraped attributes in the form of ``{ATTRIBUTE_NAME}``.
These placeholders are then replaced with the other scraped attribute string after all other processing 
steps (scraping, regex, processors).

Attribute placeholders can also be used to form **detail page URLs**. This can be used for more flexible
detail page creation, e.g. by defining a non-saved help attribute ``tmp_attr_1`` in your ``ScrapedObjClass``
definition and using a ``pre_url`` processor like ``'pre_url': 'http://someurl.org/{tmp_attr_1}'``.

.. note::
   Placeholders for detail page URLs can only be used with attributes scraped from the main page!

.. _predefined_processors:

Predefined Processors
---------------------

string_strip
^^^^^^^^^^^^
============================== ================================================================
*Description*                  Applies the python strip function to remove leading and trailing
                               characters
*Usable with other processors* Yes
*Context definition (Example)* ``'string_strip': ' .!'`` (optional, default: ' \n\t\r')
*Result (Example)*             " ... Example Text!!!" -> "Example Text"
============================== ================================================================

remove_chars
^^^^^^^^^^^^
============================== ================================================================
*Description*                  Removing of characters or character pattern using the python
                               re.sub function by providing a regex pattern
*Usable with other processors* Yes
*Context definition (Example)* ``'remove_chars': '[-\.]+'``
*Result (Example)*             "Example... Text--!--!!" -> "Example Text!!!"
============================== ================================================================

pre_string
^^^^^^^^^^
============================== ===================================================================
*Description*                  Adds a string before the scraped text
*Usable with other processors* Yes
*Context definition (Example)* ``'pre_string': 'BEFORE_'``
*Result (Example)*               "Example Text" -> "BEFORE_Example Text"
============================== ===================================================================

post_string
^^^^^^^^^^^
============================== ===================================================================
*Description*                  Appends a string after the scraped text
*Usable with other processors* Yes
*Context definition (Example)* ``'post_string': '_AFTER'``
*Result (Example)*               "Example Text" -> "Example Text_AFTER"
============================== ===================================================================

pre_url
^^^^^^^
============================== ===================================================================
*Description*                  Adding a domain to scraped url paths, works like pre_string with
                               some url specific enhancements (throwing away defined domain when
                               scraped text has a leading "http://" e.g.) 
*Usable with other processors* Yes
*Context definition (Example)* ``'pre_url': 'http://example.org/'``
*Result (Example)*               "/path/to/page.html" -> "http://example.org/path/to/page.html"
============================== ===================================================================

replace
^^^^^^^
============================== ===================================================================
*Description*                  When the scraper succeeds in scraping the attribute value, the text 
                               scraped is replaced with the replacement given in the processor 
                               context.
*Usable with other processors* No
*Context definition (Example)* ``'replace': 'This is a replacement'``
*Result (Example)*               "This text was scraped" -> "This is a replacement"
============================== ===================================================================

substr_replace
^^^^^^^^^^^^^^
============================== ===================================================================
*Description*                  A substring occurring one or multiple times in the scraped element 
                               is replaced by a target string provided (Strings are separated by
                               a ":" char, for use in text please mask ":" char like this: "\:" ).
*Usable with other processors* Yes
*Context definition (Syntax)*  ``'substr_replace': '[SUBSTRING]:[TARGET STRING]'``
*Context definition (Example)* ``'substr_replace': 'Title\: Hello:New Title\: Hi'``
*Result (Example)*               "Title: Hello my dear friend" -> "New Title: Hi my dear friend"
============================== ===================================================================

static
^^^^^^
============================== ===================================================================
*Description*                  No matter if the scraper succeeds in scraping the attribute value 
                               or not, the static value is used as an attribute value. This 
                               processor is also useful for testing for not relying on too many 
                               x_path values having to succeed at once.
*Usable with other processors* No
*Context definition (Example)* ``'static': 'Static text'``
*Result (Example)*             "No matter if this text was scraped or not" -> "Static text"
============================== ===================================================================

date
^^^^
============================== ===================================================================
*Description*                  Tries to parse a date with Python's strptime function
                               (extra sugar: recognises 'yesterday', 'gestern', 'today', 'heute',
                               'tomorrow', 'morgen')
*Usable with other processors* Yes
*Context definition (Example)* ``'date': '%d.%m.%Y'``
*Result (Example)*             "04.12.2011" -> "2011-12-04"
============================== ===================================================================

time
^^^^
============================== ===================================================================
*Description*                  Tries to parse a time with Python's strptime function
*Usable with other processors* Yes
*Context definition (Example)* ``'time': '%H hours %M minutes'``
*Result (Example)*             "22 hours 15 minutes" -> "22:15"
============================== ===================================================================

ts_to_date
^^^^^^^^^^
============================== ===================================================================
*Description*                  Tries to extract the local date of a unix timestamp
*Usable with other processors* Yes
*Context definition (Example)* No context definition
*Result (Example)*             "1434560700" -> "2015-06-17"
============================== ===================================================================

ts_to_time
^^^^^^^^^^
============================== ===================================================================
*Description*                  Tries to extract the local time of a unix timestamp
*Usable with other processors* Yes
*Context definition (Example)* No context definition
*Result (Example)*             "1434560700" -> "19:05:00"
============================== ===================================================================

duration
^^^^^^^^
============================== ===================================================================
*Description*                  Tries to parse a duration, works like time processor but with
                               time unit overlap breakdown
*Usable with other processors* Yes
*Context definition (Example)* ``'duration': '%M Minutes'``
*Result (Example)*             "77 Minutes" -> "01:17:00"
============================== ===================================================================

.. _custom_processors:

Custom Processors
-----------------

If the existing predefined processors don't fit your needs you can write your own custom processors.

A processor is just a simple Python function taking a string as input (the scraped data) together
with the context information provided in the Django admin and return a somehow modified string.

To get an idea how processors work have a look at the predefined processors in the 
``dynamic_scraper.utils.processors`` module.

To tell ``DDS`` about your custom processors provide the path(s) to your processor module(s) via the
:ref:`setting_dscraper_custom_processors` setting.

