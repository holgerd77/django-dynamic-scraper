===========
Development
===========

.. _contribute:

How to contribute
=================

You can contribute to improve Django Dynamic Scraper in many ways:

* If you stumbled over a bug or have suggestions for an improvements or a feature addition report 
  an issue on the GitHub page with a good description.
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

**Changes in version 0.11.0-beta** (2016-05-13)

* First major release version with support for new ``Scrapy 1.0+`` structure
  (only ``Scrapy 1.1`` officially supported)
* From this release on older Scrapy versions like ``0.24`` are not supported any more,
  please update your Scrapy version!
* Beta ``Python 3`` support
* Support for ``Django 1.9``

* The following manual adoptions in your project are necessary:

  * Scrapy's ``DjangoItem`` class has now moved from ``scrapy.contrib.djangoitem``
    to a separate repository ``scrapy-djangoitem`` 
    ( `see Scrapy docs <http://doc.scrapy.org/en/1.0/news.html#full-list-of-relocations>`_). 
    The package has to be separately
    installed with ``pip install scrapy-djangoitem`` and the import in your ``models.py``
    class has to be changed to ``from scrapy_djangoitem import DjangoItem`` 
    (see: :ref:`creatingdjangomodels`)
  * Due to Scrapy`s switch to Python`s build-in logging functionality the logging calls
    in your custom pipeline class have to be slightly changed, removing the 
    ``from scrapy import log`` import and changing the ``log.[LOGLEVEL]`` attribute
    handover in the log function call to ``logging.[LOGLEVEL]``
    (see: :ref:`adding_pipeline_class`)
  * Change ``except IntegrityError, e:`` to ``except IntegrityError as e:`` in your custom
    ``pipelines.py`` module (see: :ref:`adding_pipeline_class`)

* Following changes have been made:

  * Changed logging to use Python's build-in ``logging`` module
  * Updated import paths according to Scrapy release documentation
  * Running most of the unit tests in parallel batches (when using the shell scripts)
    to speed up test runs
  * Updated ``django-celery`` version requirement to ``3.1.17`` to work with ``Django 1.9``
  * Updated open_news example fixture, introduction of versioned fixture data dumps
  * Removed dependency on ``scrapy.xlib.pydispatch`` being removed in ``Scrapy 1.1`` 
    (former ``DDS v.0.10`` releases will break with ``Scrapy 1.1``)

* If you use ``Scrapy/Splash`` for ``Javascript`` rendering:

  * Updated dependencies, replaced ``scrapyjs`` with ``scrapy-splash`` (renaming),
    please update your dependencies accordingly!

* Bugfixes:

  * Fixed bug with ``DSCRAPER_IMAGES_STORE_FORMAT`` set to ``THUMBS`` not working correctly

**Changes in version 0.10.0-beta EXPERIMENTAL** (2016-01-27)

* Experimental release branch no longer maintained, please see release notes for ``0.11``.

**Changes in version 0.9.6-beta** (2016-01-26)

* Fixed a severe bug causing scrapers to break when scraping unicode text
* Making unicode text scraping more robust
* Added several unit tests testing unicode string scraping/usage in various contexts
* Reduce size of textarea fields in scraper definitions
* Added order attribute for scraped object attributes for convenience when editing scrapers
  (see: :ref:`defining_scraped_object_class`)
* New migration ``0017``, run Django ``migrate`` command

**Changes in version 0.9.5-beta** (2016-01-18)

* Fixed a severe bug when using non-saved detail page URLs in scrapers

**Changes in version 0.9.4-beta** (2016-01-15)

* Fixed a critical bug when using non-saved fields for scraping leading to incorrect data attribution to items

**Changes in version 0.9.3-beta** (2016-01-14)

* New command line options ``output_num_mp_response_bodies`` and ``output_num_dp_response_bodies``
  for logging the complete response bodies of the first {Int} main/detail page responses to the screen
  for debugging (for the really hard cases :-)) (see: :ref:`running_scrapers`)

**Changes in version 0.9.2-beta** (2016-01-14)

* New processor ``remove_chars`` (see: :ref:`processors`) for removing one or several type of chars from
  a scraped string

**Changes in version 0.9.1-beta** (2016-01-13)

* Allowing empty ``x_path`` scraper attribute fields for easier appliance of ``static`` processor to fill
  in static values
* Enlargening ``x_path``, ``reg_exp`` and ``processor`` fields in Django admin scraper definition from
  ``CharField`` to ``TextField`` for more extensive ``x_path``, ``reg_exp`` and ``processor`` definitions
  and more comfortable input/editing
* New command line option ``max_pages_read`` for limiting the number of pages read on test runs
  (see: :ref:`running_scrapers`)
* New migration ``0016``, run Django ``migrate`` command

**Changes in version 0.9.0-beta** (2016-01-11)

* BREAKING!!! This release slighly changes the semantics of the internal ``ValidationPipeline`` class
  in ``dynamic_scraper/pipelines.py`` to also pass items to your custom user pipeline when the
  ``do_action`` command line parameter (see: :ref:`running_scrapers`) is not set. This creates the need
  of an additional ``if spider.conf['DO_ACTION']:`` restriction in your custom user pipeline function 
  (see: :ref:`adding_pipeline_class`). Make sure to add this line, otherwise you will get unwanted side
  effects. If you do more stuff in your custom pipeline class also have a broader look if this new
  behaviour changes your processing (you should be save though if you apply the ``if`` restriction above
  to all of your code in the classs).
* Decoupling of ``DDS`` ``Django`` item save mechanism for the pipeline processing to allow the usage
  of Scrapy`s build-in output options ``--output=FILE`` and ``--output-format=FORMAT`` to scrape items 
  into a file instead of the DB (see: :ref:`running_scrapers`).
* The above is the main change, not touching too much code. Release number nevertheless jumped up a whole
  version number to indicate a major breaking change in using the library!
* Another reason for the new ``0.9`` version number is the amount of new features being added throuhout
  minor ``0.8`` releases (more flexible checker concept, monitoring functionality, attribute placeholders)
  to point out the amount of changes since ``0.8.0``.  

**Changes in version 0.8.13-beta** (2016-01-07)

* Expanded detail page URL processor placeholder concept to generic attribute placeholders (:ref:`attribute_placeholders`)
* Unit test for new functionality

**Changes in version 0.8.12-beta** (2016-01-06)

* Fixed ``Clone Scraper`` Django admin action omitting the creation of ``RequestPageType`` and ``Checker``
  objects introduced in the ``0.8`` series
* Narrowing the requirements for ``Pillow`` to ``3.x`` versions to reduce possible future side effects

**Changes in version 0.8.11-beta** (2016-01-05)

* New :ref:`attribute_placeholders` (previously: detail page URL placeholder) which can be used for more flexible detail page URL creation
* Unit test for new functionality

**Changes in version 0.8.10-beta** (2015-12-04)

* New ``--with-next-alert`` flag for monitoring management cmds to reduce amount of mail alerts,
  see updated :ref:`monitoring` section for details
* More verbose output for monitoring management cmds
* New migration ``0015``, run Django ``migrate`` command

**Changes in version 0.8.9-beta** (2015-12-01)

* Minor changes

**Changes in version 0.8.8-beta** (2015-12-01)

* Fixed a bug in ``Django admin`` from previous release

**Changes in version 0.8.7-beta** (2015-12-01)

* New syntax/semantics of management commands ``check_last_checker_deletes`` 
  and ``check_last_scraper_saves``
* Added ``last_scraper_save_alert_period`` and ``last_checker_delete_alert_period`` alert period fields 
  for scraper, new migration ``0014``, run Django ``migrate`` command
* New fields are used for providing time periods for the lowest accepted value for last scraper saves and checker deletes,
  these values are then checked by the management commands above (see: :ref:`monitoring`)
* Older timestamps for current values of a scraper for ``last_scraper_save`` and ``last_checker_delete`` also 
  trigger a visual warning indication in the Django admin scraper overview page

**Changes in version 0.8.6-beta** (2015-11-30)

* Two new management commands ``check_last_checker_deletes`` and ``check_last_scraper_saves`` which can be run as a cron job
  for basic scraper/checker monitoring (see: :ref:`monitoring`)

**Changes in version 0.8.5-beta** (2015-11-30)

* New ``last_scraper_save``, ``last_checker_delete`` ``datetime`` attributes for ``Scraper`` model for monitoring/
  statistis purposes (can be seen on ``Scraper`` overview page in ``Django admin``)
* New migration ``0013``, run Django ``migrate`` command

**Changes in version 0.8.4-beta** (2015-11-27)

Starting update process for ``Python 3`` support with this release (not there yet!)

* Fixed severe bug in ``task_utils.py`` preventing checker scheduling to work
* New dependency on `Python-Future 0.15+ <http://python-future.org/>`_ to support integrated ``Python 2/3`` code base,
  please install with ``pip install future``
* Updating several files for being ``Python 2/3`` compatible

**Changes in version 0.8.3-beta** (2015-10-01)

* More flexible checker concept now being an own ``Checker`` model class and allowing for more than one checker for a
  single scraper. This allows checking for different URLs or xpath conditions.
* Additional comment fields for ``RequestPageTypes`` and ``Checkers`` in admin for own notes
* Adopted unit tests to reflect new checker structure
* ``self.scrape_url = self.ref_object.url`` assignment in checker python class not used any more 
  (see: :ref:`creating_checker_class`), you might directly want to remove this from your project class
  definition to avoid future confusion
* Some docs rewriting for Checker creation (see: :ref:`item_checkers`)
* New migrations ``0011``, ``0012``, run Django ``migrate`` command

**Changes in version 0.8.2-beta** (2015-09-24)

* Fixed bug preventing checker tests to work
* Added Javascript rendering to checkers
* Fixed a bug letting checkers/checker tests choose the wrong detail page URL for checking under certain circumstances

**Changes in version 0.8.1-beta** (2015-09-22)

* Fixed packaging problem not including custom static Django admin JS file (for ``RequestPageType`` admin form collapse/expand)

**Changes in version 0.8.0-beta** (2015-09-22)

* New request page types for main page and detail pages of scrapers (see: :ref:`adding_request_page_types`):

  * Cleaner association of request options like content or request type to main or detail pages (see: :ref:`advanced_request_options`)
  * More flexibility in using different request options for main and detail pages (rendering Javascript on main but not on 
    detail pages, different HTTP header or body values,...)
  * Allowance of several detail page URLs per scraper
  * Possibility for not saving the detail page URL used for scraping by unchecking corresponding new ``ScrapedObjClass`` 
    attribute ``save_to_db``

* ATTENTION! This release comes with heavy internal changes regarding both DB structure and scraping logic.
  Unit tests are running through, but there might be untested edge cases. If you want to use the new functionality in a production 
  environment please do this with extra care. You also might want to wait for 2-3 weeks after release
  and/or for a following 0.8.1 release (not sure if necessary yet). If you upgrade it is HIGHLY RECOMMENDED TO BACKUP YOUR
  PROJECT AND YOUR DB before!
* Replaced Scrapy ``Spider`` with ``CrawlSpider`` class being the basis for ``DjangoBaseSpider``, allowing
  for more flexibility when extending
* Custom migration for automatically creating new ``RequestPageType`` objects for existing scrapers
* Unit tests for new functionality
* Partly restructured documentation, separate :ref:`installation` section
* Newly added ``static`` files, run Django ``collectstatic`` command (collaps/expand for ``RequestPageType`` inline admin form)
* New migrations ``0008``, ``0009``, ``0010``, run Django ``migrate`` command

**Changes in version 0.7.3-beta** (2015-08-10)

* New attribute ``dont_filter`` for ``Scraper`` request options (see: :ref:`advanced_request_options`), necessary
  for some scenarios where ``Scrapy`` falsely marks (and omits) requests as being duplicate (e.g. when scraping uniform
  URLs together with custom HTTP header pagination)
* Fixed bug preventing processing of ``JSON`` with non-string data types (e.g. ``Number``) for scraped attributes,
  values are now automatically converted to ``String``
* New migration ``0007``, run Django ``migrate`` command

**Changes in version 0.7.2-beta** (2015-08-06)

* Added new ``method`` attribute to ``Scraper`` not binding HTTP method choice (``GET``/``POST``) so strictly to choice of ``request_type``
  (allowing e.g. more flexible ``POST`` requests), see: :ref:`advanced_request_options`
* Added new ``body`` attribute to ``Scraper`` allowing for sending custom request ``HTTP message body`` data, see:
  :ref:`advanced_request_options`
* Allowing ``pagination`` for ``headers``, ``body`` attributes
* Allowing of ``ScrapedObjectClass`` definitions in ``Django admin`` with no attributes defined as ``ID field``
  (omits double checking process when used)
* New migration ``0006``, run Django ``migrate`` command

**Changes in version 0.7.1-beta** (2015-08-03)

* Fixed severe bug preventing ``pagination`` for ``cookies`` and ``form_data`` to work properly
* Added a new section in the docs for :ref:`advanced_request_options`
* Unit tests for some scraper request option selections

**Changes in version 0.7.0-beta** (2015-07-31)

* Adding additional HTTP header attributes to scrapers in Django admin
* Cookie support for scrapers
* Passing Scraper specific Scrapy meta data
* Support for form requests, passing form data within requests
* Pagination support for cookies, form data
* New migration ``0005``, run Django ``migrate`` command
* All changes visible in Scraper form of Django admin
* ATTENTION! While unit tests for existing functionality all passing through, new functionality is not heavily
  tested yet due to problems in creating test scenarios. If you want to use the new functionality in a production 
  environment please test with extra care. You also might want to wait for 2-3 weeks after release
  and/or for a following 0.7.1 release (not sure if necessary yet)
* Please report problems/bugs on `GitHub <https://github.com/holgerd77/django-dynamic-scraper>`_.

**Changes in version 0.6.0-beta** (2015-07-14)

* Replaced implicit and static ID concept of mandatory ``DETAIL_PAGE_URL`` type attribute serving as ID with a more
  flexible concept of explicitly setting ``ID Fields`` for ``ScrapedObjClass`` in ``Django`` admin 
  (see: :ref:`defining_scraped_object_class`)
* New attribute ``id_field`` for ``ScrapedObjClass``, please run Django ``migrate`` command (migration ``0004``)
* ``DETAIL_PAGE_URL`` type attribute not necessary any more when defining the scraped object class allowing for more
  scraping use cases (classic and simple/flat datasets not referencing a certain detail page)
* Single ``DETAIL_PAGE_URL`` type ``ID Field`` still necessary for using ``DDS`` checker functionality
  (see: :ref:`item_checkers`)
* Additional form checks for ``ScrapedObjClass`` definition in ``Django`` admin

**Changes in version 0.5.2-beta** (2015-06-18)

* Two new processors ``ts_to_date`` and ``ts_to_time`` to extract local date/time from unix timestamp string (see: :ref:`processors`)

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

[THIS ROADMAP IS PARTIALLY OUTDATED!]

**pre-alpha**

Django Dynamic Scraper's pre-alpha phase was meant to be for
people interested having a first look at the library and give some feedback if things were making generally 
sense the way they were worked out/conceptionally designed or if a different approach on implementing 
some parts of the software would have made more sense.

**alpha**

DDS is currently in alpha stadium, which means that the library has proven itself in (at least) one 
production environment and can be (cautiously) used for production purposes. However being still very
early in develpment, there are still API and DB changes for improving the lib in different ways.
The alpha stadium will
be used for getting most parts of the API relatively stable and eliminate the most urgent bugs/flaws
from the software.

**beta (current)**

In the beta phase the API of the software should be relatively stable, though occasional changes will
still be possible if necessary. The beta stadium should be the first period where it is save to use
the software in production and beeing able to rely on its stability. Then the software should remain in
beta for some time.

**Version 1.0**

Version 1.0 will be reached when the software has matured in the beta phase and when at least 10+ 
projects are using DDS productively for different purposes.
