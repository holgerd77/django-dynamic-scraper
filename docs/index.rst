.. django-dynamic-scraper documentation master file, created by
   sphinx-quickstart on Mon Dec  5 15:05:19 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-dynamic-scraper - Documentation
======================================

Django Dynamic Scraper (DDS) is an app for Django build on top of the scraping framework Scrapy_. While preserving many
of the features of Scrapy it lets you dynamically create and manage spiders via the Django admin interface.


Features
--------

* Create and manage scrapers for your Django models in the Django admin interface
* Many features of Scrapy_ like regular expressions, processors, pipelines (see `Scrapy Docs`_)
* Image/screenshot scraping
* Dynamic scheduling depending on crawling success via Django Celery
* Checkers to check if items once scraped are still existing

.. note::
   DDS v.0.3 now officially supports ``Scrapy v.0.16.x`` (``Scrapy v.0.18.x`` is not working yet)!

.. _Scrapy: http://www.scrapy.org 
.. _`Scrapy Docs`: http://doc.scrapy.org


User Manual
-----------

.. toctree::
   :maxdepth: 2
   
   getting_started
   advanced_topics
   basic_services
   reference
   development


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`