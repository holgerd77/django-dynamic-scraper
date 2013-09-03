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


Running the test suite
======================
Testing Django Dynamic Scraper - especially the scraper runs - is a bit tricky since Scrapy uses the 
networking engine `Twisted <http://twistedmatrix.com/>`_ for running scrapers, which can't be restarted
in the same process. So running most of the test classes as Django tests via `python manage.py test` will
fail. The easiest way I found to work around this was to create a shell script `run_tests.sh` which invokes
single test methods where scrapers are involved separately so that a new process for every test run is started.

For running the tests first go to the `tests` directory and start a test server with::

	./testserver.sh
	
Then you can run the test suite with::

	./run_tests.sh


.. _releasenotes:

Release Notes
=============

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
