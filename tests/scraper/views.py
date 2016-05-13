from __future__ import unicode_literals
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def request_type_method(request, test_case):
    if request.method == 'POST':
        return redirect('/static/site_generic/event_main.html')
    else:
        return HttpResponse('Not a POST request!')


@csrf_exempt
def header_body_data(request, test_case):
    if test_case == 'header':
        if 'HTTP_REFERER' in request.META and request.META['HTTP_REFERER'] == 'http://comingfromhere.io':
            return redirect('/static/site_generic/event_main.html')
    if test_case == 'body':
        if request.body == b'This is the HTTP request body content.':
            return redirect('/static/site_generic/event_main.html')

    return HttpResponse('Test case not found!')


@csrf_exempt
def form_data(request, test_case):
    if 'simple' in request.POST:
        if request.POST['simple'] == 'SIMPLE_VALUE':
            return redirect('/static/site_generic/event_main.html')
    
    if 'page' in request.POST:
        if request.POST['page'] == '1':
            return redirect('/static/site_generic/event_main1.html')
        if request.POST['page'] == '2':
            return redirect('/static/site_generic/event_main2.html')
    
    return HttpResponse('Form data not found!')


def cookies(request, test_case):

    if test_case == 'simple':
        if 'simple' in request.COOKIES and request.COOKIES['simple'] == 'SIMPLE_VALUE':
            return redirect('/static/site_generic/event_main.html')
        else:
            return HttpResponse('Cookie not found!')
    else:
        raise Http404

