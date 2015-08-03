from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^form_data/(?P<test_case>\w+).html$', views.form_data),
    url(r'^cookies/(?P<test_case>\w+).html$', views.cookies),
]