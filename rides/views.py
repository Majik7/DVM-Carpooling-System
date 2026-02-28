from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

# Create your views here.

@login_required
def passenger_dashboard(request):
    if not(request.user.is_passenger):
        raise PermissionDenied
    return HttpResponse("<h1>ehhehehe</h1>")

@login_required
def driver_dashboard(request):
    if not(request.user.is_driver):
        raise PermissionDenied
    return HttpResponse("<h1>ehhehehe</h1>")