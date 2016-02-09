from __future__ import unicode_literals
from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^scraper/', include('scraper.urls')),
]
