===============
Getting started
===============



Introduction
============

With Django Dynamic Scraper (DDS) you can define your Scrapy_ scrapers dynamically via the Django admin interface
and save your scraped items in the database you defined for your Django project.
Since it simplifies things DDS is not usable for all kinds of scrapers, but it is well suited for the relatively
common case of regularly scraping a website with a list of updated items (e.g. news, events, etc.) and than dig 
into the detail page to scrape some more infos for each item.

Here are some examples for some use cases of DDS:
Build a scraper for ...

* Local music events for different event locations in your city
* New organic recipes for asian food
* The latest articles from blogs covering fashion and style in Berlin
* ...Up to your imagination! :-)

Django Dynamic Scraper tries to keep its data structure in the database as separated as possible from the 
models in your app, so it comes with its own Django model classes for defining scrapers, runtime information
related to your scraper runs and classes for defining the attributes of the models you want to scrape.
So apart from a few foreign key relations your Django models stay relatively independent and you don't have
to adjust your model code every time DDS's model structure changes.   

The DDS repository on GitHub contains an example project in the ``example_project`` folder, showing how to 
create a scraper for open news content on the web (starting with Wikinews_ from Wikipedia). The source code
from this example is used in the following guidelines.

.. _Scrapy: http://www.scrapy.org 
.. _Wikinews: http://en.wikinews.org/wiki/Main_Page
.. _GitHub: https://github.com/holgerd77/django-dynamic-scraper

Installation
============

.. _requirements:

Requirements
------------
The **basic requirements** for Django Dynamic Scraper are:

* Python 2.7+ (earlier versions untested, Python 3.x not yet supported)
* `Django <https://www.djangoproject.com/>`_ 1.7/1.8 (newer versions untested)
* Scrapy_ 0.20-0.24 (newer versions untested)
* `Python JSONPath RW 1.4+ <https://github.com/kennknowles/python-jsonpath-rw>`_

If you want to use the **scheduling mechanism** of DDS you also have to install ``django-celery``:

* `django-celery <http://ask.github.com/django-celery/>`_ 3.1.16 (newer versions untested)

For **scraping images** you will need the Pillow Library:

* `Pillow Libray (PIL fork) 2.5+ <https://python-pillow.github.io/>`_

Since ``v.0.4.1`` ``DDS`` has basic ``ScrapyJS/Splash`` support for rendering/processing ``Javascript`` before
scraping the page. For this to work you have to install and configure (see: :ref:`setting_up_scrapyjs_splash`) ``ScrapyJS``:

* `ScrapyJS 0.1+ <https://github.com/scrapinghub/scrapyjs>`_ 

.. note::
   ``DDS 0.4`` version and upwards have dropped ``South`` support and using the internal migration system
   from ``Django 1.7+``, south migrations can still be found in ``dynamic_scraper/south_migrations`` folder though. If you are upgrading from a DDS version older than ``0.3.2`` make sure to apply all the ``South`` migrations first
   and the do an initial fake migration for switching to the Django migration system (see also Django docs on
   migrations)!

.. _release_compatibility:

Release Compatibility Table
---------------------------
Have a look at the following table for an overview which ``Django``, ``Scrapy`` and ``django-celery`` versions are supported
by which ``DDS`` version. Due to dev resource constraints backwards compatibility for older ``Django`` or ``Scrapy`` releases for new
``DDS`` releases normally can not be granted.

+-------------+-------------------------------+---------------------------------------+-------------------------+
| DDS Version | Django                        | Scrapy                                | django-celery           |
+=============+===============================+=======================================+=========================+
| 0.4/0.5     | 1.7/1.8 (newer untested)      | 0.22/0.24 (newer untested)            | 3.1.16 (newer untested) |
+-------------+-------------------------------+---------------------------------------+-------------------------+
| 0.3         | 1.4-1.6                       | 0.16/0.18 (recommended)               | 3.0+ (3.1+ untested)    |
+-------------+-------------------------------+---------------------------------------+-------------------------+
|             | (1.7+ unsupported)            | 0.20/0.22/0.24 (dep. warnings)        |                         |
+-------------+-------------------------------+---------------------------------------+-------------------------+
| 0.2         | 1.4 (1.5+ unsupported)        | 0.14 (0.16+ unsupported) 2.x          | (3.0 untested)          |
+-------------+-------------------------------+---------------------------------------+-------------------------+

.. note::
   Please get in touch (GitHub_) if you have any additions to this table. A library version is counted as supported if the
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

.. _creatingdjangomodels:

Creating your Django models
===========================

Create your model classes
-------------------------

When you want to build a Django app using Django Dynamic Scraper to fill up your models with data you have
to provide *two model classes*. The *first class* stores your scraped data, in our news example this is a
class called ``Article`` storing articles scraped from different news websites. 
The *second class* is a reference class for this first model class, defining where
the scraped items belong to. Often this class will represent a website, but it could also represent a 
category, a topic or something similar. In our news example we call the class ``NewsWebsite``. Below is the
code for this two model classes::

	from django.db import models
	from dynamic_scraper.models import Scraper, SchedulerRuntime
	from scrapy.contrib.djangoitem import DjangoItem
	
	
	class NewsWebsite(models.Model):
	    name = models.CharField(max_length=200)
	    url = models.URLField()
	    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)
	    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
	    
	    def __unicode__(self):
	        return self.name
	
	
	class Article(models.Model):
	    title = models.CharField(max_length=200)
	    news_website = models.ForeignKey(NewsWebsite) 
	    description = models.TextField(blank=True)
	    url = models.URLField()
	    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)
	    
	    def __unicode__(self):
	        return self.title
	
	
	class ArticleItem(DjangoItem):
	    django_model = Article

As you can see, there are some foreign key fields defined in the models referencing DDS models.
The ``NewsWebsite`` class has a reference to the :ref:`scraper` DDS model, which contains the main
scraper with information about how to scrape the attributes of the article objects. The ``scraper_runtime``
field is a reference to the :ref:`scheduler_runtime` class from the DDS models. An object of this class stores 
scheduling information, in this case information about when to run a news website scraper for the next time. 
The ``NewsWebsite`` class also has to provide the url to be used during the scraping process. You can either
use (if existing) the representative url field of the model class, which is pointing to the nicely-layouted
overview news page also visited by the user. In this case we are choosing this way with taking the ``url``
attribute of the model class as the scrape url. However, it often makes sense to provide a dedicated ``scrape_url``
(you can name the attribute freely) field for cases, when the representative url differs from the scrape url
(e.g. if list content is loaded via ajax, or if you want to use another format of the content - e.g. the rss
feed - for scraping).

The ``Article`` class to store scraped news articles also has a reference to the :ref:`scheduler_runtime` DDS
model class called ``checker_runtime``. In this case the scheduling object holds information about the next 
existance check (using the ``url`` field from ``Article``) to evaluate if the news article
still exists or if it can be deleted (see :ref:`item_checkers`).

Last but not least: Django Dynamic Scraper uses the DjangoItem_ class from Scrapy for
being able to directly store the scraped data into the Django DB. You can store the item class 
(here: ``ArticleItem``) telling Scrapy which model class to use for storing the data directly underneath the
associated model class.

.. note::
   For having a loose coupling between your runtime objects and your domain model objects you should declare
   the foreign keys to the DDS objects with the ``blank=True, null=True, on_delete=models.SET_NULL``
   field options. This will prevent a cascading delete of your reference object as well as the associated
   scraped objects when a DDS object is deleted accidentally.

Deletion of objects
-------------------

If you delete model objects via the Django admin interface, the runtime objects are not
deleted as well. If you want this to happen, you can use Django's 
`pre_delete signals <https://docs.djangoproject.com/en/dev/topics/db/models/#overriding-model-methods>`_
in your ``models.py`` to delete e.g. the ``checker_runtime`` when deleting an article::

	@receiver(pre_delete)
	def pre_delete_handler(sender, instance, using, **kwargs):
	    ....
	    
	    if isinstance(instance, Article):
	        if instance.checker_runtime:
	            instance.checker_runtime.delete()
	            
	pre_delete.connect(pre_delete_handler)


.. _DjangoItem: https://scrapy.readthedocs.org/en/latest/topics/djangoitem.html

Defining the object to be scraped
=================================

If you have done everything right up till now and even synced your DB :-) your Django admin should look 
similar to the following screenshot below, at least if you follow the example project:

.. image:: images/screenshot_django-admin_overview.png

Before being able to create scrapers in Django Dynamic Scraper you have to define which parts of the Django
model class you defined above should be filled by your scraper. This is done via creating a new 
:ref:`scraped_obj_class` in your Django admin interface and then adding several :ref:`scraped_obj_attr` 
datasets to it, which is done inline in the form for the :ref:`scraped_obj_class`. The attributes for the
object class have to be named like the attributes in your model class to be scraped. In our open news example
we want the title, the description, and the url of an Article to be scraped, so we add these attributes with
the corresponding names to the scraped obj class.

The reason why we are redefining these attributes here, is that we can later define x_path elements for each
of theses attributes dynamically in the scrapers we want to create. When Django Dynamic Scraper
is scraping items, the **general workflow of the scraping process** is as follows:

* The DDS scraper is scraping base elements from the overview page of items beeing scraped, with each base
  element encapsulating an item summary, e.g. in our open news example an article summary containing the
  title of the article, a screenshot and a short description. The encapsuling html tag often is a ``div``,
  but could also be a ``td`` tag or something else.
* Then the DDS scraper is scraping the url from this item summary block, which leads to the detail page of the item
* All the real item attributes (like a title, a description, a date or an image) are then scraped either from 
  within the item summary block on the overview page or from the detail page of the item. This can be defined later
  when creating the scraper itself.

To define which of the scraped obj attributes are just simple standard attributes to be scraped, which one
is the base attribute (this is a bit of an artificial construct) and which one is the url to be followed
later, we have to choose an attribute type for each attribute defined. There is a choice between the following
types (taken from ``dynamic_scraper.models.ScrapedObjAttr``)::

	ATTR_TYPE_CHOICES = (
	    ('S', 'STANDARD'),
	    ('T', 'STANDARD (UPDATE)'),
	    ('B', 'BASE'),
	    ('U', 'DETAIL_PAGE_URL'),
	    ('I', 'IMAGE'),
	)

``STANDARD``, ``BASE`` and ``DETAIL_PAGE_URL`` should be clear by now, ``STANDARD (UPDATE)`` behaves like ``STANDARD``, 
but these attributes are updated with the new values if the item is already in the DB. ``IMAGE`` represents attributes which will 
hold images or screenshots. So for our open news example we define a base attribute called 'base' with 
type ``BASE``, two standard elements 'title' and 'description' with type ``STANDARD`` 
and a url field called 'url' with type ``DETAIL_PAGE_URL``. Your definition form for your scraped obj class 
should look similar to the screenshot below:

.. image:: images/screenshot_django-admin_add_scraped_obj_class.png

.. note::
   If you define an attribute as ``STANDARD (UPDATE)`` attribute and your scraper reads the value for this attribute from the detail page
   of the item, your scraping process requires **much more page requests**, because the scraper has to look at all the detail pages
   even for items already in the DB to compare the values. If you don't use the update functionality, use the simple ``STANDARD``
   attribute instead!


.. note::
	Though it is a bit of a hack: if you want to **scrape items on a website not leading to detail pages** you can do
	this by defining another (non url) field as the ``DETAIL_PAGE_URL`` field, e.g. a title or an id. Make sure that this
	field is unique since the ``DETAIL_PAGE_URL`` field is also used as an identifier for preventing double
	entries in the DB and don't use the ``from_detail_page`` option in your scraper definitions. It is also not possible
	to use checkers with this workaround. However: it works, I even wrote a unit test for this hack! :-)

Defining your scrapers
======================

General structure of a scraper
------------------------------

Scrapers for Django Dynamic Scraper are also defined in the Django admin interface. You first have to give the
scraper a name and select the associated :ref:`scraped_obj_class`. In our open news example we call the scraper
'Wikinews Scraper' and select the :ref:`scraped_obj_class` named 'Article' defined above.

The main part of defining a scraper in DDS is to create several scraper elements, each connected to a 
:ref:`scraped_obj_attr` from the selected :ref:`scraped_obj_class`. Each scraper element define how to extract 
the data for the specific :ref:`scraped_obj_attr` by following the main concepts of Scrapy_ for scraping
data from websites. In the fields named 'x_path' and 'reg_exp' an XPath and (optionally) a regular expression
is defined to extract the data from the page, following Scrapy's concept of 
`XPathSelectors <http://readthedocs.org/docs/scrapy/en/latest/topics/selectors.html>`_. The 'from_detail_page'
check box tells the scraper, if the data for the object attibute for the scraper element should be extracted
from the overview page or the detail page of the specific item. The fields 'processors' and 'processors_ctxt' are
used to define output processors for your scraped data like they are defined in Scrapy's
`Item Loader section <http://readthedocs.org/docs/scrapy/en/latest/topics/loaders.html>`_.
You can use these processors e.g. to add a string to your scraped data or to bring a scraped date in a
common format. More on this later. Finally, the 'mandatory' check box is indicating whether the data
scraped by the scraper element is a necessary field. If you define a scraper element as necessary and no
data could be scraped for this element the item will be dropped. Note, that you always have to keep attributes
mandatory, if the corresponding attributes of your domain model class is a mandatory field, otherwise the 
scraped item can't be saved in the DB.

For the moment, keep the ``status`` to ``MANUAL`` to run the spider via the command line during this tutorial.
Later you will change it to ``ACTIVE``. 

Creating the scraper of our open news example
---------------------------------------------

Let's use the information above in the context of our Wikinews_ example. Below you see a screenshot of an
html code extract from the Wikinews_ overview page like it is displayed by the developer tools in Google's 
Chrome browser:
 
.. image:: images/screenshot_wikinews_overview_page_source.png

The next screenshot is from a news article detail page:

.. image:: images/screenshot_wikinews_detail_page_source.png

We will use these code snippets in our examples.

.. note::
	If you don't want to manually create the necessary DB objects for the example project, you can also run
	``python manage.py loaddata open_news/open_news.json`` from within the ``example_project`` directory in your 
	favorite shell to have all the objects necessary for the example created automatically .
	
.. note::
   The WikiNews site changes its code from time to time. I will try to update the example code and text in the
   docs, but I won't keep pace with the screenshots so they can differ slightly compared to the real world example.

1. First we have to define a base 
scraper element to get the enclosing DOM elements for news item
summaries. On the Wikinews_ overview page all news summaries are enclosed by ``<td>`` tags with a class
called 'l_box', so ``//td[@class="l_box"]`` should do the trick. We leave the rest of the field for the 
scraper element on default.

2. It is not necessary but just for the purpose of this example let's scrape the title of a news article
from the article detail page. On an article detail page the headline of the article is enclosed by a
``<h1>`` tag with an id named 'firstHeading'. So ``//h1[@id="firstHeading"]/span/text()`` should give us the headline.
Since we want to scrape from the detail page, we have to activate the 'from_detail_page' check box.

3. All the standard elements we want to scrape from the overview page are defined relative to the
base element. Therefore keep in mind to leave the trailing double slashes of XPath definitions.
We scrape the short description of a news item from within a ``<span>`` tag with a class named 'l_summary'.
So the XPath is ``p/span[@class="l_summary"]/text()``.

4. And finally the url can be scraped via the XPath ``span[@class="l_title"]/a/@href``. Since we only scrape 
the path of our url with this XPath and not the domain, we have to use a processor for the first time to complete
the url. For this purpose there is a predefined processor called 'pre_url'. You can find more predefined
processors in the ``dynamic_scraper.utils.processors`` module. 'pre_url' is simply doing what we want,
namely adding a base url string to the scraped string. To use a processor, just write the function name
in the processor field. Processors can be given some extra information via the processors_ctxt field.
In our case we need the spefic base url our scraped string should be appended to. Processor context
information is provided in a dictionary like form: ``'processor_name': 'context'``, in our case:
``'pre_url': 'http://en.wikinews.org'``. Together with our scraped string this will create
the complete url.

.. image:: images/screenshot_django-admin_scraper_1.png
.. image:: images/screenshot_django-admin_scraper_2.png

This completes our scraper. The form you have filled out should look similar to the screenshot above 
(which is broken down to two rows due to space issues).

.. note::
   You can also **scrape** attributes of your object **from outside the base element** by using the ``..`` notation
   in your XPath expressions to get to the parent nodes!

.. _json_jsonpath_scrapers:

Creating scrapers for JSON/Usage of JSONPath
--------------------------------------------

Beside creating ``HTML`` or ``XML`` scrapers where you can use classic ``XPath`` notation, ``DDS`` supports also scraping pages encoded in ``JSON`` (``v.0.5.0`` and above), e.g. for crawling web APIs or ajax call result pages.

For scraping ``JSON``, ``JSONPath`` is used, an ``XPath``-like expression language for digging into ``JSON``.
For reference see expressions as defined here:

* `GitHub - python-jsonpath-rw Library <https://github.com/kennknowles/python-jsonpath-rw>`_
* `JSONPath - XPath for JSON <http://goessner.net/articles/JsonPath/>`_

.. note::
   Using ``JSONPath`` in ``DDS`` works for standard ``JSON`` page results, but is not as heavily tested as using
   ``XPath`` for data extraction. If you are working with more complex ``JSONPath`` queries and run into problems,
   please report them on GitHub_!

Create the domain entity reference object (NewsWebsite) for our open news example
---------------------------------------------------------------------------------

Now - finally - we are just one step away of having all objects created in our Django admin.
The last dataset we have to add is the reference object of our domain, meaning a ``NewsWebsite``
object for the Wikinews Website.

To do this open the NewsWebsite form in the Django admin, give the object a meaningful name ('Wikinews'),
assign the scraper and create an empty :ref:`scheduler_runtime` object with ``SCRAPER`` as your
``runtime_type``. 

.. image:: images/screenshot_django-admin_add_domain_ref_object.png

.. _settingupscrapypython:

Setting up Scrapy/Create necessary python modules for your app
==============================================================

Now after having created the Django models we want to scrape and having created the scraper and associated
objects in the database we have to set up Scrapy and get it to work together with the stuff we have created.
To get this going, we have to create a new Scrapy project, adjust some settings in the configuration and create
two short python module files, one with a spider class, inheriting from :ref:`django_spider`, and a finalising
pipeline for saving our scraped objects.

.. _setting_up_scrapy:

Setting up Scrapy
-----------------

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
-------------------------------------

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

Adding the spider class
-----------------------

The main work left to be done in our spider class - which is inheriting from the :ref:`django_spider` class
of Django Dynamic Scraper - is to instantiate the spider by connecting the domain model classes to it
in the ``__init__`` function::

	from dynamic_scraper.spiders.django_spider import DjangoSpider
	from open_news.models import NewsWebsite, Article, ArticleItem
	
	
	class ArticleSpider(DjangoSpider):
	    
	    name = 'article_spider'
	
	    def __init__(self, *args, **kwargs):
	        self._set_ref_object(NewsWebsite, **kwargs)
	        self.scraper = self.ref_object.scraper
	        self.scrape_url = self.ref_object.url
	        self.scheduler_runtime = self.ref_object.scraper_runtime
	        self.scraped_obj_class = Article
	        self.scraped_obj_item_class = ArticleItem
	        super(ArticleSpider, self).__init__(self, *args, **kwargs)

.. _adding_pipeline_class:

Adding the pipeline class
-------------------------

Since you maybe want to add some extra attributes to your scraped items, DDS is not saving the scraped items
for you but you have to do it manually in your own item pipeline::

	from django.db.utils import IntegrityError
	from scrapy import log
	from scrapy.exceptions import DropItem
	from dynamic_scraper.models import SchedulerRuntime
	
	class DjangoWriterPipeline(object):
	    
	    def process_item(self, item, spider):
	        try:
	            item['news_website'] = spider.ref_object
	            
	            checker_rt = SchedulerRuntime(runtime_type='C')
	            checker_rt.save()
	            item['checker_runtime'] = checker_rt
	            
	            item.save()
	            spider.action_successful = True
	            spider.log("Item saved.", log.INFO)
	                
	        except IntegrityError, e:
	            spider.log(str(e), log.ERROR)
	            raise DropItem("Missing attribute.")
	                
	        return item 

The things you always have to do here is adding the reference object to the scraped item class and - if you
are using checker functionality - create the runtime object for the checker. You also have to set the
``action_successful`` attribute of the spider, which is used internally by DDS when the spider is closed.

.. _running_scrapers:

Running/Testing your scraper
============================

You can run/test spiders created with Django Dynamic Scraper from the command line similar to how you would run your
normal Scrapy spiders, but with some additional arguments given. The syntax of the DDS spider run command is
as following::

	scrapy crawl SPIDERNAME -a id=REF_OBJECT_ID 
	                        [-a do_action=(yes|no) -a run_type=(TASK|SHELL) 
	                        -a max_items_read={Int} -a max_items_save={Int}]
	
* With ``-a id=REF_OBJECT_ID`` you provide the ID of the reference object items should be scraped for,
  in our example case that would be the Wikinews ``NewsWebsite`` object, probably with ID 1 if you haven't
  added other objects before. This argument is mandatory.
  
* By default, items scraped from the command line are not saved in the DB. If you want this to happen,
  you have to provide ``-a do_action=yes``.
  
* With ``-a run_type=(TASK|SHELL)`` you can simulate task based scraper runs invoked from the 
  command line. This can be useful for testing, just leave this argument for now.

* With ``-a max_items_read={Int}`` and ``-a max_items_save={Int}`` you can override the scraper settings for these
  params.

So, to invoke our Wikinews scraper, we have the following command::

	scrapy crawl article_spider -a id=1 -a do_action=yes
	

If you have done everything correctly (which would be a bit unlikely for the first run after so many single steps,
but just in theory... :-)), you should get some output similar to the following, of course with other 
headlines: 

.. image:: images/screenshot_scrapy_run_command_line.png

In your Django admin interface you should now see the scraped articles listed on the article overview page:

.. image:: images/screenshot_django-admin_articles_after_scraping.png

Phew.

Your first scraper with Django Dynamic Scraper is working. Not so bad! If you do a second run and there
haven't been any new bugs added to the DDS source code in the meantime, no extra article objects should be added
to the DB. If you try again later when some news articles changed on the Wikinews overview page, the new
articles should be added to the DB. 





