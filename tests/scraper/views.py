from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def form_data(request, test_case):
    if test_case == 'simple':
        if 'simple' in request.POST and request.POST['simple'] == 'SIMPLE_VALUE':
            return redirect('/static/site_generic/event_main.html')
        else:
            return HttpResponse('Cookie not found!')
    else:
        raise Http404


def cookies(request, test_case):

    if test_case == 'simple':
        if 'simple' in request.COOKIES and request.COOKIES['simple'] == 'SIMPLE_VALUE':
            return redirect('/static/site_generic/event_main.html')
        else:
            return HttpResponse('Cookie not found!')
    else:
        raise Http404

