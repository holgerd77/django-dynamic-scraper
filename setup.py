from setuptools import setup

import os

setup(
    name='django-dynamic-scraper',
    version='0.8.3',
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
    #install_requires=[
    #    'Django>=1.7,<1.9',
    #    'Scrapy>=0.22.0,<0.25',
    #    'scrapyd',
    #    'jsonpath-rw>=1.4',
    #    'django-celery==3.1.16', # Scheduling
    #    'pillow',
    #],
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
