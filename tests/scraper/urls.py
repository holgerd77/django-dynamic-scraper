from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^request_type_method/(?P<test_case>\w+).html$', views.request_type_method),
    url(r'^header_body_data/(?P<test_case>\w+).html$', views.header_body_data),
    url(r'^form_data/(?P<test_case>\w+).html$', views.form_data),
    url(r'^cookies/(?P<test_case>\w+).html$', views.cookies),
]