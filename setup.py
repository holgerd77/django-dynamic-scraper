from setuptools import setup

import os

setup(
    name='django-dynamic-scraper',
    version='0.12.4',
    description='Creating Scrapy scrapers via the Django admin interface',
    author='Holger Drewes',
    author_email='Holger.Drewes@gmail.com',
    url='https://github.com/holgerd77/django-dynamic-scraper/',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='BSD License',
    platforms=['OS Independent'],
    packages=[
        'dynamic_scraper',
        'dynamic_scraper.management',
        'dynamic_scraper.management.commands',
        'dynamic_scraper.migrations',
        'dynamic_scraper.south_migrations',
        'dynamic_scraper.spiders',
        'dynamic_scraper.utils',
    ],
    package_data = {
        'dynamic_scraper': [
            'static/js/*',
        ],
    },
    install_requires=[
    #    Django, Scrapy and Celery requirements are commented out here and have
    #    to be installed manually to avoid side-effects when updating the software.
    #    Version numbers are updated accordingly though.
    #    'Django>=1.8,<1.12',
    #    'Scrapy>=1.1,<1.5',
    #    'scrapy-djangoitem>=1.1.1,<1.2',
    #    'scrapy-splash>=0.7', # Optional
    #    'scrapyd>=1.2,<1.3',
        'jsonpath-rw>=1.4',
    #    'kombu>=3.0.37,<3.1',
    #    'Celery==3.1.25',
    #    'django-celery==3.2.1', # Scheduling
        'future>=0.15,<0.16',
        'pillow>=3.0,<4.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
