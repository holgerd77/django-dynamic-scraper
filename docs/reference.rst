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

TODO

.. _scraper_elem:

ScraperElem
-----------

TODO

.. _scraper_runtime:

ScraperRuntime
--------------

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