.. django-dynamic-scraper documentation master file, created by
   sphinx-quickstart on Mon Dec  5 15:05:19 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-dynamic-scraper - Documentation
======================================

Django Dynamic Scraper (DDS) is an app for Django build on top of the scraping framework Scrapy_. While preserving many
of the features of Scrapy it lets you dynamically create and manage spiders via the Django admin interface.

.. note::
   Lot's of new features added recently :

   * ``Django 1.9``/``Scrapy 1.1`` support
   * Beta ``Python 3`` support
   * ``Javascript`` rendering
   * Scraping ``JSON`` content
   * More flexible ID and detail page URL(s) concept
   * Several checkers for a single scraper
   * Custom ``HTTP Header/Body``, ``Cookies``, ``GET/POST`` requests
   * ``Scrapy Meta`` attributes
   * Scraper/Checker ``Monitoring``

   See :ref:`releasenotes` for further details!

Features
--------

* Create and manage scrapers for your Django models in the Django admin interface
* Many features of Scrapy_ like regular expressions, processors, pipelines (see `Scrapy Docs`_)
* Image/screenshot scraping
* Dynamic scheduling depending on crawling success via Django Celery
* Checkers to check if items once scraped are still existing


.. _Scrapy: http://www.scrapy.org 
.. _`Scrapy Docs`: http://doc.scrapy.org


User Manual
-----------

.. toctree::
   :maxdepth: 2
   
   introduction
   installation
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