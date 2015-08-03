from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^cookies/(?P<test_case>\w+).html$', views.cookies),
]