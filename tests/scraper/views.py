from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render


def cookies(request, test_case):

    if test_case == 'simple':
        if 'simple' in request.COOKIES and request.COOKIES['simple'] == 'SIMPLE_VALUE':
            return redirect('/static/site_generic/event_main.html')
        else:
            return HttpResponse('Cookie not found!')
    else:
        raise Http404

