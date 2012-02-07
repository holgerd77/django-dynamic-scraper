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


DSCRAPER_LOG_ENABLED
--------------------
Default: ``True``

Enable/disable the DDS logging (see :ref:`logging` for more info).

DSCRAPER_LOG_LEVEL
------------------
Default: ``ERROR``

Set the log level for DDS logging. Possible values are CRITICAL, ERROR, WARNING, INFO and DEBUG.

DSCRAPER_LOG_LIMIT
------------------
Default: ``250``

The number of log entries in the Django database table.


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

TODO

.. _django_checker:

DjangoChecker
-------------

TODO


Processors
==========

TODO

replace
-------
============================== ===================================================================
*Description*                  When the scraper succeeds in scraping the attribute value, the text 
                               scraped is replaced with the replacement given in the processor 
                               context.
*Usable with other processors* No
*Context definition (Example)* ``'replace': 'This is a replacement'``
*Result (Example)*               "This text was scraped" -> "This is a replacement"
============================== ===================================================================

static
------
============================== ===================================================================
*Description*                  No matter if the scraper succeeds in scraping the attribute value 
                               or not, the static value is used as an attribute value. This 
                               processor is also useful for testing for not relying on too many 
                               x_path values having to succeed at once.
*Usable with other processors* No
*Context definition (Example)* ``'static': 'Static text'``
*Result (Example)*             "No matter if this text was scraped or not" -> "Static text"
============================== ===================================================================

TODO
