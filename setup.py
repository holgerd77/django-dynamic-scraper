from setuptools import setup

import os

setup(
    name='django-dynamic-scraper',
    version='0.1',
    description='Creating Scrapy scrapers via the Django admin interface.',
    author='Holger Drewes',
    author_email='Holger.Drewes@googlemail.com',
    url='https://github.com/holgerd77/django-dynamic-scraper/',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    packages=[
        'dynamic_scraper',
        'dynamic_scraper.spiders',
        'dynamic_scraper.utils',
    ],
    #install_requires=[
        #'Django>=1.2',
        #'Scrapy>=0.14',
        # Scheduling
        #'django-kombu',
        #'django-celery',
    #],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
