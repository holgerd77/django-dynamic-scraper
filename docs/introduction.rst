Introduction
============

With Django Dynamic Scraper (DDS) you can define your `Scrapy <http://www.scrapy.org>`_ scrapers dynamically via the Django admin interface
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
create a scraper for open news content on the web (starting with `Wikinews <http://en.wikinews.org/wiki/Main_Page>`_ 
from Wikipedia). The source code from this example is used in the :ref:`getting_started` guide.