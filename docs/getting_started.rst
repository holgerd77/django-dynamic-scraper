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

.. warning::
	While there is a testsuite for DDS with tests for most of its' features and the app runs relatively stable,
	DDS is **pre-alpha** and still in an early development phase. Expect API changes in future releases 
	which will require manual adaption in your code. During pre-alpha phase, API and/or DB changes can also
	occur after minor release updates (e.g. from 0.1.0 to 0.1.1).  


.. _Scrapy: http://www.scrapy.org 
.. _Wikinews: http://en.wikinews.org/wiki/Main_Page

Installation
============

Requirements
------------
The **basic requirements** for Django Dynamic Scraper are:

* Python 2.7+ (earlier versions untested)
* `Django <https://www.djangoproject.com/>`_ 1.3+ (earlier versions untested)
* Scrapy_ 0.14+ (necessary)

If you want to use the **scheduling mechanism** of DDS you also have to install ``django-celery`` and 
``django-kombu``. You should be able to use another messaging framework/store than ``django-kombu``
but this is untested and ``django-kombu`` is the easiest choice which normally should be sufficient
for the simple purpose it is serving here.

* `django-celery <http://ask.github.com/django-celery/>`_ 2.4+ (earlier versions untested)
* `django-kombu <https://github.com/ask/django-kombu>`_ 0.9+ (earlier versions untested)

For **scraping images** you will also need the Python Image Library:

* `Python Image Libray (PIL) 1.1.7+ <http://www.pythonware.com/products/pil/>`_ (earlier versions untested)

..
	And finally: DDS is using ``South`` for **migrations in the DB schema** between different versions
	(e.g. if a new attribute is added to a model class). If you don't exactly know what ``South`` is and
	what it does, it is highly recommended that you take the (relatively short) time to learn how to use it.
	Since DDS is in an early development stage, it is very likely that the DB schema will change in the
	future, and using ``South`` instead of ``syncdb`` to create and update your DB schema will make your
	life a lot easier if you want to keep pace with the latest versions of DDS:

	* `South 0.7+ <http://south.aeracode.org/>`_ (earlier versions untested) 

.. note::
   Please drop a note if you have tested DDS with older versions of the libraries above!

Installation/Configuration
--------------------------
For installing Django Dynamic Scraper you have to first met the requirements above. You can do this by
manually installing the libraries you need with ``pip`` or ``easy_install``, which may be a better choice
if you e.g. don't want to risk your Django installation to be touched during the installation process. 
However if you are sure that there
is no danger ahead or if you are running DDS in a new ``virtualenv`` environment, you can install all the
requirements above together with::

	pip install -r requirements.txt
	
Then download the DDS source code from GitHub and either add the ``dynamic_scraper`` folder to your 
``PYTHONPATH`` or your project manually or install DDS with::

	python setup.py install
	
Note, that the requirements are NOT included in the ``setup.py`` script since this caused some problems 
when testing the installation and the requirements installation process with ``pip`` turned out to be
more stable.
	
Now, to use DDS in your Django project add ``'dynamic_scraper'`` to your ``INSTALLED_APPS`` in your
project settings.


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
	from dynamic_scraper.models import Scraper, ScraperRuntime, SchedulerRuntime
	from scrapy.contrib_exp.djangoitem import DjangoItem
	
	
	class NewsWebsite(models.Model):
	    name = models.CharField(max_length=200)
	    scraper_runtime = models.ForeignKey(ScraperRuntime, blank=True, null=True, on_delete=models.SET_NULL)
	    
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

As you can see, there is one foreign key field defined in each model referencing DDS models.
The ``NewsWebsite`` class has a reference to the :ref:`scraper_runtime` DDS model, which saves the runtime
information about the scraping process, e.g. the url to be scraped or information if the scraper is active 
or not. 

The ``Article`` class to store scraped news articles also has one extra mandatory field called ``checker_runtime``,
referencing the :ref:`scheduler_runtime` class from the DDS models. An object of this class stores 
scheduling information, in this case information about the next existance check (using the ``url`` field from
``Article``) to evaluate if the news article
still exists or if it can be deleted (see :ref:`item_checkers`).

Last but not least: Django Dynamic Scraper uses the (still experimental (!)) DjangoItem_ class from Scrapy for
being able to directly store the scraped data into the Django DB. You can store the item class 
(here: ``ArticleItem``) telling Scrapy which model class to use for storing the data directly underneath the
associated model class.

.. note::
   For having a loose coupling between your runtime objects and your domain model objects you should declare
   the foreign keys to the runtime objects with the ``blank=True, null=True, on_delete=models.SET_NULL``
   field options. This will prevent a cascading delete of your reference object as well as the associated
   scraped objects when a scraper_runtime object is deleted accidentally.

Deletion of objects
-------------------

If you delete model objects via the Django admin interface, the runtime objects are not
deleted as well. If you want this to happen, you have to to add a handler reacting to 
Django's `pre_delete signals <https://docs.djangoproject.com/en/dev/topics/db/models/#overriding-model-methods>`_
to your ``models.py`` file::

	from django.db.models.signals import pre_delete
	from django.dispatch import receiver
	
	@receiver(pre_delete)
	def pre_delete_handler(sender, instance, using, **kwargs):
	    if isinstance(instance, NewsWebsite) and instance.scraper_runtime:
	        instance.scraper_runtime.delete()
	    if isinstance(instance, Article) and instance.checker_runtime:
	        instance.checker_runtime.delete()

.. _DjangoItem: http://readthedocs.org/docs/scrapy/en/latest/experimental/djangoitems.html

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
* Then the DDS scrpaer is scraping the url from this item summary block, which leads to the detail page of the item
* All the real item attributes (like a title, a description, a date or an image) are then scraped either from 
  within the item summary block on the overview page or from the detail page of the item. This can be defined later
  when creating the scraper itself.

To define which of the scraped obj attributes are just simple standard attributes to be scraped, which one
is the base attribute (this is a bit of an artificial construct) and which one is the url to be followed
later, we have to choose an attribute type for each attribute defined. There is a choice between the following
types (taken from ``dynamic_scraper.models.ScrapedObjAttr``)::

	ATTR_TYPE_CHOICES = (
	    ('S', 'STANDARD'),
	    ('B', 'BASE'),
	    ('U', 'FOLLOW_URL'),
	    ('I', 'IMAGE'),
	)

``STANDARD``, ``BASE`` and ``FOLLOW_URL`` should be clear by now, ``IMAGE`` represents attributes which will 
hold images or screenshots. So for our open news example we define a base attribute called 'base' with 
type ``BASE``, two standard elements 'title' and 'description' with type ``STANDARD`` 
and a url field called 'url' with type ``FOLLOW_URL``. Your definition form for your scraped obj class 
should look similar to the screenshot below:

.. image:: images/screenshot_django-admin_add_scraped_obj_class.png



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
`XPathSelectors <http://readthedocs.org/docs/scrapy/en/latest/topics/selectors.html>`_. The 'follow_url'
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

1. First we have to define a base 
scraper element to get the enclosing DOM elements for news item
summaries. On the Wikinews_ overview page all news summaries are enclosed by ``<td>`` tags with a class
called 'l_box', so ``//td[@class="l_box"]`` should do the trick. We leave the rest of the field for the 
scraper element on default.

2. It is not necessary but just for the purpose of this example let's scrape the title of a news article
from the article detail page. On an article detail page the headline of the article is enclosed by a
``<h1>`` tag with an id named 'firstHeading'. So ``//h1[@id="firstHeading"]/text()`` should give us the headline.
Since we want to scrape from the detail page, we have to activate the 'follow_url' check box.

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

This completes our scraper. The form you have filled out should look similar to this (broken down to
two rows due to space issues):

.. image:: images/screenshot_django-admin_scraper_1.png
.. image:: images/screenshot_django-admin_scraper_2.png

In addition to our scraper we also need a :ref:`scraper_runtime` to run our scraper. To create a 
:ref:`scraper_runtime` object in your django admin, create a :ref:`scheduler_runtime` object first,
leaving all the values in their default state. Than create a :ref:`scraper_runtime` object, 
giving it a meaningful name ('Wikinews Runtime'), assign the created scheduler runtime
object as well as the created scraper to it and save the scraper runtime object.


Create the domain entity reference object (NewsWebsite) for our open news example
---------------------------------------------------------------------------------

Now - finally - we are just one step away of having all objects created in our Django admin.
The last dataset we have to add is the reference object of our domain, meaning a NewsWebsite
object for the Wikinews Website.

To do this open the NewsWebsite form in the Django admin, give the object a meaningful name ('Wikinews')
and assign the scraper runtime created before.    

.. image:: images/screenshot_django-admin_add_domain_ref_object.png


Setting up Scrapy/Create necessary python modules for your app
==============================================================

Now after having created the Django models we want to scrape and having created the scraper and associated
objects in the database we have to set up Scrapy and get it to work together with the stuff we have created.
To get this going, we have to create a new Scrapy project, adjust some settings in the configuration and create
two short python module files, one with a spider class, inheriting from :ref:`django_spider`, and a finalising
pipeline for saving our scraped objects.

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
	
	[deploy]
	#url = http://localhost:6800/
	project = open_news


And this is your ``settings.py`` file::

	import sys
	import os.path
	
	PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
	sys.path = sys.path + [os.path.join(PROJECT_ROOT, '../../..'), os.path.join(PROJECT_ROOT, '../..')]
	
	from django.core.management import setup_environ
	import example_project.settings
	setup_environ(example_project.settings)

	BOT_NAME = 'open_news'
	BOT_VERSION = '1.0'
	
	SPIDER_MODULES = ['open_news.scraper']
	NEWSPIDER_MODULE = 'open_news.scraper'
	USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
	
	ITEM_PIPELINES = [
	    'dynamic_scraper.pipelines.ValidationPipeline',
	    'open_news.scraper.pipelines.DjangoWriterPipeline',
	]

The ``SPIDER_MODULES`` and ``NEWSPIDER_MODULE`` settings are referencing our ``scraper`` package where
Scrapy will find the (yet to be written) spider module. For the ``ITEM_PIPELINES`` setting we have to
add (at least) two pipelines. The first one is the mandatory pipeline from DDS, doing stuff like checking
for the mandatory attributes we have defined in our scraper in the DB or preventing double entries already
existing in the DB (identified by the url attribute of your scraped items) to be saved a second time.  

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
	        self.scraper_runtime = self.ref_object.scraper_runtime
	        self.scraped_obj_class = Article
	        self.scraped_obj_item_class = ArticleItem
	        super(ArticleSpider, self).__init__(self, *args, **kwargs)

TODO

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
	            
	            checker_rt = SchedulerRuntime()
	            checker_rt.save()
	            item['checker_runtime'] = checker_rt
	            
	            item.save()
	            spider.action_successful = True
	            spider.log("Item saved.", log.INFO)
	                
	        except IntegrityError, e:
	            spider.log(str(e), log.ERROR)
	            raise DropItem("Missing attribute.")
	                
	        return item 

TODO


Running/Testing your scraper
============================

You can run/test spiders created with Django Dynamic Scraper from the command line similar to how you would run your
normal Scrapy spiders, but with some additional arguments given. The syntax of the DDS spider run command is
as following::

	scrapy crawl SPIDERNAME -a id=REF_OBJECT_ID [-a do_action=(yes|no) -a run_type=(TASK|SHELL)]
	
* With ``-a id=REF_OBJECT_ID`` you provide the ID of the reference object items should be scraped for,
  in our example case that would be the Wikinews ``NewsWebsite`` object, probably with ID 1 if you haven't
  added other objects before. This argument is mandatory.
  
* By default, items scraped from the command line are not saved in the DB. If you want this to happen,
  you have to provide ``-a do_action=yes``.
  
* And with the ``-a run_type=(TASK|SHELL)`` you can simulate task based scraper runs invoked from the 
  command line. This can be useful for testing, just leave this argument for now.
  
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





