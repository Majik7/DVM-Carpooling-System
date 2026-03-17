from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .forms import NewTripForm
from . import utils
from .models import Trip, RouteNode

# Create your views here.

@login_required
def passenger_dashboard(request):
    if not(request.user.is_passenger):
        raise PermissionDenied
    return HttpResponse("<h1>Passenger Dashboard</h1>")

@login_required
def driver_dashboard(request):
    if not(request.user.is_driver):
        raise PermissionDenied
    else:
        ongoing_rides = Trip.objects.filter(driver = request.user, status = 'O')
        completed_rides = Trip.objects.filter(driver = request.user, status = 'C')

        return render(request, 'rides/driver_dash.html', context = {
            'ongoing_trips': ongoing_rides,
            'completed_trips': completed_rides,
            'driver': request.user,
        })

@login_required
def new_ride(request):
    if not request.user.is_driver:
        raise PermissionDenied
    if request.method == 'POST':
        form = NewTripForm(request.POST)

        if form.is_valid():
            start_node = form.cleaned_data['start_node']
            end_node = form.cleaned_data['end_node']
            max_passengers = form.cleaned_data['max_passengers']

            path = utils.create_path(start_node, end_node)

            trip = Trip.objects.create(start_node = start_node,
                                       end_node = end_node,
                                       max_passengers = max_passengers,
                                       driver = request.user)
            
        for i, node in enumerate(path):
            RouteNode.objects.create(trip = trip, node = node, order = i)
        
        return redirect('rides:driver_dashboard')
    else:
        form = NewTripForm()

    return render(request, 'rides/new_trip.html', context = {'form': form})