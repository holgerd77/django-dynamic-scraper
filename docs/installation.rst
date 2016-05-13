.. _installation:

Installation
============

.. _requirements:

Requirements
------------
The **basic requirements** for Django Dynamic Scraper are:

* Python 2.7+ or Python 3.4+
* `Django <https://www.djangoproject.com/>`_ 1.8/1.9 (newer versions untested)
* `Scrapy <http://www.scrapy.org>`_ 1.1 (older versions like ``0.24`` not supported any more!)
* `scrapy-djangoitem <https://github.com/scrapy-plugins/scrapy-djangoitem>`_ 1.1
* `Python JSONPath RW 1.4+ <https://github.com/kennknowles/python-jsonpath-rw>`_
* `Python-Future (preparing the code base to run with Python 2/3) 0.15+ <http://python-future.org/>`_

If you want to use the **scheduling mechanism** of DDS you also have to install ``django-celery``:

* `django-celery <http://ask.github.com/django-celery/>`_ 3.1.17 (newer versions untested)

For **scraping images** you will need the Pillow Library:

* `Pillow Libray (PIL fork) 2.5+ <https://python-pillow.github.io/>`_

Since ``v.0.4.1`` ``DDS`` has basic ``ScrapyJS/Splash`` support for rendering/processing ``Javascript`` before
scraping the page. For this to work you have to install and configure (see: :ref:`setting_up_scrapyjs_splash`) ``ScrapyJS``:

* `scrapy-splash <https://github.com/scrapy-plugins/scrapy-splash>` 0.6 

.. _release_compatibility:

Release Compatibility Table
---------------------------
Have a look at the following table for an overview which ``Django``, ``Scrapy``, 
``Python`` and ``django-celery`` versions are supported by which ``DDS`` version. 
Due to dev resource constraints backwards compatibility for older ``Django`` or 
``Scrapy`` releases for new ``DDS`` releases normally can not be granted.

+-------------+-------------+----------------------+----------------------+-------------------------------+
| DDS Version | Django      | Scrapy               | Python               | django-celery/Celery/Kombu    |
+=============+=============+======================+======================+===============================+
| 0.11        | 1.8/1.9     | 1.1                  | 2.7+/3.4+            | 3.1.17/3.1.20/3.0.33          |
+-------------+-------------+----------------------+----------------------+-------------------------------+
| 0.4-0.9     | 1.7/1.8     | 0.22/0.24            | 2.7                  | 3.1.16 (newer untested)       |
+-------------+-------------+----------------------+----------------------+-------------------------------+
| 0.3         | 1.4-1.6     | 0.16/0.18            | 2.7                  | 3.0+ (3.1+ untested)          |
+-------------+-------------+----------------------+----------------------+-------------------------------+
| 0.2         | 1.4         | 0.14                 | 2.7                  | (3.0 untested)                |
+-------------+-------------+----------------------+----------------------+-------------------------------+

.. note::
   Please get in touch (`GitHub <https://github.com/holgerd77/django-dynamic-scraper>`_) if you have any additions to this table. A library version is counted as supported if the
   DDS testsuite is running through (see: :ref:`test_suite`).

Installation with Pip
---------------------
Django Dynamic Scraper can be found on the PyPI Package Index `(see package description) <http://pypi.python.org/pypi/django-dynamic-scraper>`_. 
For the installation with Pip, first install the requirements above. Then install DDS with::

    pip install django-dynamic-scraper

Manual Installation
-------------------
For manually installing Django Dynamic Scraper download the DDS source code from GitHub or clone the project with
git into a folder of your choice::

    git clone https://github.com/holgerd77/django-dynamic-scraper.git .

Then you have to met the requirements above. You can do this by
manually installing the libraries you need with ``pip`` or ``easy_install``, which may be a better choice
if you e.g. don't want to risk your Django installation to be touched during the installation process. 
However if you are sure that there
is no danger ahead or if you are running DDS in a new ``virtualenv`` environment, you can install all the
requirements above together with::

    pip install -r requirements.txt
    
Then either add the ``dynamic_scraper`` folder to your 
``PYTHONPATH`` or your project manually or install DDS with::

    python setup.py install
    
Note, that the requirements are NOT included in the ``setup.py`` script since this caused some problems 
when testing the installation and the requirements installation process with ``pip`` turned out to be
more stable.
    
Now, to use DDS in your Django project add ``'dynamic_scraper'`` to your ``INSTALLED_APPS`` in your
project settings.

.. _settingupscrapypython:

Setting up Scrapy
-----------------

.. _setting_up_scrapy:

Scrapy Configuration
^^^^^^^^^^^^^^^^^^^^

For getting Scrapy_ to work the recommended way to start a new Scrapy project normally is to create a directory
and template file structure with the ``scrapy startproject myscrapyproject`` command on the shell first. 
However, there is (initially) not so much code to be written left and the directory structure
created by the ``startproject`` command cannot really be used when connecting Scrapy to the Django Dynamic Scraper
library. So the easiest way to start a new scrapy project is to just manually add the ``scrapy.cfg`` 
project configuration file as well as the Scrapy ``settings.py`` file and adjust these files to your needs.
It is recommended to just create the Scrapy project in the same Django app you used to create the models you
want to scrape and then place the modules needed for scrapy in a sub package called ``scraper`` or something
similar. After finishing this chapter you should end up with a directory structure similar to the following
(again illustrated using the open news example)::

  example_project/
    scrapy.cfg
    open_news/
      models.py # Your models.py file
      scraper/
        settings.py
        spiders.py
        (checkers.py)
        pipelines.py
        (tasks.py)
      
Your ``scrapy.cfg`` file should look similar to the following, just having adjusted the reference to the
settings file and the project name::
  
  [settings]
  default = open_news.scraper.settings
  
  #Scrapy till 0.16
  [deploy]
  #url = http://localhost:6800/
  project = open_news

  #Scrapy with separate scrapyd (0.18+)
  [deploy:scrapyd1]
  url = http://localhost:6800/
  project = open_news 


And this is your ``settings.py`` file::

  import os
  
  PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings") #Changed in DDS v.0.3

  BOT_NAME = 'open_news'
  
  SPIDER_MODULES = ['dynamic_scraper.spiders', 'open_news.scraper',]
  USER_AGENT = '%s/%s' % (BOT_NAME, '1.0')
  
  #Scrapy 0.20+
  ITEM_PIPELINES = {
      'dynamic_scraper.pipelines.ValidationPipeline': 400,
      'open_news.scraper.pipelines.DjangoWriterPipeline': 800,
  }

  #Scrapy up to 0.18
  ITEM_PIPELINES = [
      'dynamic_scraper.pipelines.ValidationPipeline',
      'open_news.scraper.pipelines.DjangoWriterPipeline',
  ]

The ``SPIDER_MODULES`` setting is referencing the basic spiders of DDS and our ``scraper`` package where
Scrapy will find the (yet to be written) spider module. For the ``ITEM_PIPELINES`` setting we have to
add (at least) two pipelines. The first one is the mandatory pipeline from DDS, doing stuff like checking
for the mandatory attributes we have defined in our scraper in the DB or preventing double entries already
existing in the DB (identified by the url attribute of your scraped items) to be saved a second time.  

.. _setting_up_scrapyjs_splash:

Setting up ScrapyJS/Splash (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

More and more webpages only show their full information load after various ``Ajax`` calls and/or ``Javascript`` 
function processing. For being able to scrape those websites ``DDS`` supports ``ScrapyJS/Spash`` starting with 
``v.0.4.1`` for basic JS rendering/processing.

For this to work you have to install ``Splash`` (the Javascript rendering service) installed - probably via ``Docker``- 
(see `installation instructions <https://splash.readthedocs.org/en/latest/install.html>`_), and then ``ScrapyJS`` with::

    pip install scrapyjs

Afterwards follow the configuration instructions on the `ScrapyJS GitHub page <https://github.com/scrapinghub/scrapyjs#configuration>`_.

For customization of ``Splash`` args ``DSCRAPER_SPLASH_ARGS`` setting can be used (see: :ref:`settings`).

ScrapyJS can later be used via activating it for certain scrapers in the corresponding ``Django Admin`` form.

.. note::
   Resources needed for completely rendering a website on your scraping machine are vastly larger then for just
   requesting/working on the plain HTML text without further processing, so make use of ``ScrapyJS/Splash`` capability
   on when needed!

