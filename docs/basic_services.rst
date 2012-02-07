==============
Basic services
==============

.. _logging:

Logging
=======

Introduction
------------
Django Dynamic Scraper provides its own logging mechanism in addition to the build-in 
`logging from Scrapy <http://doc.scrapy.org/en/latest/topics/logging.html>`_. While
the Scrapy logging is mainly for debugging your scrapers during creation time, the
DDS logging aims to get an overview how your scheduled scraper runs are doing over
time, if scrapers and checkers defined with DDS are still working and how often 
scraper or cheker runs go wrong.

.. image:: images/screenshot_django-admin_logging.png

In the screenshot above you see an overview of the log table in the Django admin 
in which new log messages are saved. In addition context information like the 
name of the spider run or the associated reference object or scraper
is provided. By using the filtering options it is possible to track down the
messages targeted to the actual needs, e.g. you can filter all the errors
occurred while running your checkers.

Logging: When and Where
-----------------------
When DDS scrapers are run from the command line both the logging messages from
Scrapy as well as the DDS logging messages are provided. In the Django model log
table, only the DDS messages are kept.

DDS only saves the DDS log messages in the DB when running with ``run_type=TASK``
and ``do_action=yes``. This is configuration used when running scrapers or 
checkers via the scheduler. When you run your scraper via the command line you
have to provide these options manually to have your DDS log messages saved in the DB
(see :ref:`running_scrapers`) in addition to be displayed on the screen.

Configuration
-------------
You can configure DDS logging behaviour by providing some settings in your `settings.py`
configuration file (see :ref:`settings`).