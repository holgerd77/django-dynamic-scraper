===========
Development
===========

.. _contribute:

How to contribute
=================

You can contribute to improve Django Dynamic Scraper in many ways:

* If you stumbled over a bug or have suggestions for an improvements or a feature addition report 
  an issue on the GitHub page
  with a good description.
* If you have already fixed the bug or added the feature in the DDS code you can also make a pull request
  on GitHub. While I can't assure that every request will be taken over into the DDS source I will look
  at each request closely and integrate it if I fell that it's a good fit!
* Since this documentation is also available in the Github repository of DDS you can also make pull
  requests for documentation!

Here are some topics for which suggestions would be especially interesting:

* If you worked your way through the documentation and you were completely lost at some point, it would
  be helpful to know where that was.
* If there are unnecessary limitations of the Scrapy functionality in the DDS source which could be
  eliminated without adding complexity to the way you can use DDS that would be very interesting to know.

And finally: please let me know about how you are using Django Dynamic Scraper!

.. _test_suite:

Running the test suite
======================

Overview
--------
Tests for ``DDS`` are organized in a separate ``tests`` Django project in the root folder of the repository.
Due to restrictions of Scrapy's networking engine `Twisted <http://twistedmatrix.com/>`_, ``DDS`` test cases directly
testing scrapers have to be run as new processes and can't be executed sequentially via `python manage.py test`.

For running the tests first go to the `tests` directory and start a test server with::

	./testserver.sh
	
Then you can run the test suite with::

	./run_tests.sh

.. note::
   If you are testing for DDS Django/Scrapy version compatibility: there might be 2-3 tests generally not working
   properly, so if just a handful of tests don't pass have a closer look at the test output.

Django test apps
----------------
There are currently two Django apps containing tests. The ``basic`` app testing scraper unrelated functionality
like correct processor output or scheduling time calculations. These tests can be run on a per-file-level::

  python manage.py test basic.processors_test.ProcessorsTest

The ``scraper`` app is testing scraper related functionality. Tests can either be run via shell script (see above)
or on a per-test-case level like this::

  python manage.py test scraper.scraper_run_test.ScraperRunTest.test_scraper #Django 1.6+
  python manage.py test scraper.ScraperRunTest.test_scraper #Django up to 1.5

Have a look at the ``run_tests.sh`` shell script for more examples!

.. _scraper_js_tests:

Running ScrapyJS/Splash JS rendering tests
------------------------------------------
Unit tests testing ``ScrapyJS/Splash`` Javascript rendering functionality need a working ``ScrapyJS/Splash`` (docker)
installation and are therefor run separately with::

  ./run_js_tests.sh

Test cases are located in ``scraper.scraper_js_run_test.ScraperJSRunTest``. Some links:

* `Splash Documentation <http://splash.readthedocs.org/en/latest/>`_
* `ScrapyJS GitHub <https://github.com/scrapinghub/scrapyjs>`_
* `Installation of Docker on OS X with Homebrew <http://blog.javabien.net/2014/03/03/setup-docker-on-osx-the-no-brainer-way/>`_

``SPLASH_URL`` in ``scraper.settings.base_settings.py`` has to be adopted to your local installation to get this running!

Docker container can be run with::

  docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 -d scrapinghub/splash

.. note::
   For rendering websites served on ``localhost`` from within ``Docker/Splash``, you can connect to ``localhost`` outside the ``Docker container`` via ``http://10.0.2.2`` 
   (see e.g. `Stackoverflow <http://stackoverflow.com/questions/1261975/addressing-localhost-from-a-virtualbox-virtual-machine>`_).

.. _releasenotes:

Release Notes
=============
**Changes in version 0.5.1-beta** (2015-06-17)

* Make sure that ``Javascript`` rendering is only activated for pages with ``HTML`` content type

**Changes in version 0.5.0-beta** (2015-06-10)

* Support for creating ``JSON/JSONPath`` scrapers for scraping ``JSON`` encoded pages (see: :ref:`json_jsonpath_scrapers`)
* Added new separate content type choice for detail pages and checkers (e.g. main page in ``HTML``, detail page in ``JSON``)
* New Scraper model attribute ``detail_page_content_type``, please run Django ``migration`` command (migration ``0003``)
* New library dependency ``python-jsonpath-rw 1.4+`` (see :ref:`requirements`)
* Updated unit tests to support/test ``JSON`` scraping

**Changes in version 0.4.2-beta** (2015-06-05)

* Possibility to customize ``Splash`` args with new setting ``DSCRAPER_SPLASH_ARGS`` (see: :ref:`setting_up_scrapyjs_splash`)

**Changes in version 0.4.1-beta** (2015-06-04)

* Support for ``Javascript`` rendering of scraped pages via ``ScrapyJS/Splash``
* Feature is optional and needs a working ScrapyJS/Splash deployment, see :ref:`requirements` and 
  :ref:`setting_up_scrapyjs_splash`
* New attribute ``render_javascript`` for ``Scraper`` model, run ``python manage.py migrate dynamic_scraper`` to
  apply (migration ``0002``)
* New unit tests for Javascript rendering (see: :ref:`scraper_js_tests`)

**Changes in version 0.4.0-beta** (2015-06-02)

* Support for ``Django 1.7/1.8`` and ``Scrapy 0.22/0.24``. Earlier versions not supported any more from this release on,
  if you need another configuration have a look at the ``DDS 0.3.x`` branch (new features won't be back-ported though)
  (see :ref:`release_compatibility`)
* Switched to Django migrations, removed ``South`` dependency
* Updated core library to work with ``Django 1.7/1.8`` (``Django 1.6`` and older not working any more)
* Replaced deprecated calls logged when run under ``Scrapy 0.24`` (``Scrapy 0.20`` and older not working any more)
* Things to consider when updating Scrapy: new ``ITEM_PIPELINES`` dict format, standalone ``scrapyd`` with changed 
  ``scrapy.cfg`` settings and new deployment procedure (see: :ref:`setting_up_scrapy`)
* Adopted ``example_project`` and ``tests`` Django projects to work with the updated dependecies
* Updated ``open_news.json`` example project fixture
* Changed ``DDS`` status to ``Beta``

**Changes in version 0.3.14-alpha** (2015-05-30)

* Pure documentation update release to get updated ``Scrapy 0.20/0.22/.24`` compatibility info in the
  docs (see: :ref:`release_compatibility`)

**Changes in version 0.3.13-alpha** (2015-05-29)

* Adopted test suite to pass through under ``Scrapy 0.18`` (Tests don't work with ``Scrapy 0.16`` any more)
* Added ``Scrapy 0.18`` to release compatibility table (see: :ref:`release_compatibility`)

**Changes in version 0.3.12-alpha** (2015-05-28)

* Added new release compatibility overview table to docs (see: :ref:`release_compatibility`)
* Adopted ``run_tests.sh`` script to run with ``Django 1.6``
* Tested ``Django 1.5``, ``Django 1.6`` for compatibility with ``DDS v.0.3.x``
* Updated title xpath in fixture for Wikinews example scraper

**Changes in version 0.3.11-alpha** (2015-04-20)

* Added ``only-active`` and ``--report-only-erros`` options to ``run_checker_tests`` management command (see: :ref:`run_checker_tests`)

**Changes in version 0.3.10-alpha** (2015-03-17)

* Added missing management command for checker functionality tests to distribution (see: :ref:`run_checker_tests`)

**Changes in version 0.3.9-alpha** (2015-01-23)

* Added new setting ``DSCRAPER_IMAGES_STORE_FORMAT`` for more flexibility with storing original and/or thumbnail images (see :ref:`scraping_images`)

**Changes in version 0.3.8-alpha** (2014-10-14)

* Added ability for ``duration`` processor to break down and parse second values greater than one hour in total
  (>= 3600 seconds) (see: :ref:`processors`)


**Changes in version 0.3.7-alpha** (2014-03-20)

* Improved ``run_checker_tests`` management command with ``--send-admin-mail`` flag for usage of command in
  cronjob (see: :ref:`run_checker_tests`) 

**Changes in version 0.3.6-alpha** (2014-03-19)

* Added new admin action clone_scrapers to get a functional copy of scrapers easily

**Changes in version 0.3.5-alpha** (2013-11-02)

* Add super init method to call init method in Scrapy BaseSpider class to DjangoBaseSpider init method (see `Pull Request #32 <https://github.com/holgerd77/django-dynamic-scraper/pull/32>`_)

**Changes in version 0.3.4-alpha** (2013-10-18)

* Fixed bug displaying wrong message in checker tests
* Removed ``run_checker_tests`` celery task (which wasn't working anyway) and replaced it with
  a simple Django management command ``run_checker_tests`` to run checker tests for all scrapers


**Changes in version 0.3.3-alpha** (2013-10-16)

* Making status list editable in Scraper admin overview page for easier status change for many scrapers at once
* Possibility to define ``x_path`` checkers with blank ``checker_x_path_result``, the checker is then succeeding if
  elements are found on page (before this lead to an error message)   

**Changes in version 0.3.2-alpha** (2013-09-28)

* Fixed the exception when scheduler string was processed (see `Pull Request #27 <https://github.com/holgerd77/django-dynamic-scraper/pull/27>`_)
* Allowed Checker Reference URLs to be longer than the the default 200 characters (DB Migration ``0004``, see `Pull Request #29 <https://github.com/holgerd77/django-dynamic-scraper/pull/29>`_)
* Changed ``__unicode__`` method for ``SchedulerRuntime`` to prevent ``TypeError`` (see `Google Groups Discussion <https://groups.google.com/forum/#!topic/django-dynamic-scraper/FSNUGhFY7YY>`_)
* Refer to ``ID`` instead of ``PK`` (see `commit in nextlanding repo <https://github.com/nextlanding/django-dynamic-scraper/commit/c4dfaa6e167293c7d35188c8f94f08974a32f310>`_) 

**Changes in version 0.3.1-alpha** (2013-09-03)

* Possibility to add keyword arguments to spider and checker task method to specify which reference objects
  to use for spider/checker runs (see: :ref:`definetasks`)

**Changes in version 0.3-alpha** (2013-01-15)

* Main purpose of release is to upgrade to new libraries (Attention: some code changes necessary!)
* ``Scrapy 0.16``: The ``DjangoItem`` class used by DDS moved from ``scrapy.contrib_exp.djangoitem``
  to ``scrapy.contrib.djangoitem``. Please update your Django model class accordingly (see: :ref:`creatingdjangomodels`).
* ``Scrapy 0.16``: ``BOT_VERSION`` setting no longer used in Scrapy/DDS ``settings.py`` file (see: :ref:`settingupscrapypython`)
* ``Scrapy 0.16``: Some minor import changes for DDS to get rid of deprecated settings import
* ``Django 1.5``: Changed Django settings configuration, please update your Scrapy/DDS ``settings.py`` file (see: :ref:`settingupscrapypython`)
* ``django-celery 3.x``: Simpler installation, updated docs accordingly (see: :ref:`installingcelery`)
* New log output about which Django settings used when running a scraper

**Changes in version 0.2-alpha** (2012-06-22)

* Substantial API and DB layout changes compared to version 0.1
* Introduction of South for data migrations
 

**Changes in version 0.1-pre-alpha** (2011-12-20)

* Initial version


Roadmap
=======

**pre-alpha**

Django Dynamic Scraper's pre-alpha phase was meant to be for
people interested having a first look at the library and give some feedback if things were making generally 
sense the way they were worked out/conceptionally designed or if a different approach on implementing 
some parts of the software would have made more sense.

**alpha (current)**

DDS is currently in alpha stadium, which means that the library has proven itself in (at least) one 
production environment and can be (cautiously) used for production purposes. However being still very
early in develpment, there are still API and DB changes for improving the lib in different ways.
The alpha stadium will
be used for getting most parts of the API relatively stable and eliminate the most urgent bugs/flaws
from the software.

**beta**

In the beta phase the API of the software should be relatively stable, though occasional changes will
still be possible if necessary. The beta stadium should be the first period where it is save to use
the software in production and beeing able to rely on its stability. Then the software should remain in
beta for some time.

**Version 1.0**

Version 1.0 will be reached when the software has matured in the beta phase and when at least 10+ 
projects are using DDS productively for different purposes.
