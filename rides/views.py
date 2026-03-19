from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .forms import NewTripForm, CarpoolRequestForm
from . import utils
from .models import Trip, RouteNode, CarpoolRequest, Offer
from rest_framework.decorators import api_view
from accounts.models import Transaction
from rest_framework.response import Response
from rest_framework import status
from network.models import Node
from .serializers import CarpoolRequestSerializer

# Create your views here.

@login_required
def passenger_dashboard(request):
    if not request.user.is_passenger:
        raise PermissionDenied
    
    active_requests = CarpoolRequest.objects.filter(passenger=request.user, status='P')
    confirmed_requests = CarpoolRequest.objects.filter(passenger=request.user, status='C')
    cancelled_requests = CarpoolRequest.objects.filter(passenger=request.user, status='X')
    
    return render(request, 'rides/passenger_dash.html', {
        'active_requests': active_requests,
        'confirmed_requests': confirmed_requests,
        'cancelled_requests': cancelled_requests,
        'passenger': request.user
    })

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

            if path:
                trip = Trip.objects.create(
                    start_node=start_node,
                    end_node=end_node,
                    max_passengers=max_passengers,
                    driver=request.user
                )
                
                for i, node in enumerate(path):
                    RouteNode.objects.create(trip=trip, node=node, order=i)
                
                return redirect('rides:driver_dashboard')
            else:
                form.add_error(None, "No valid route exists between these nodes.")
    else:
        form = NewTripForm()

    return render(request, 'rides/new_trip.html', {'form': form})

@login_required
def cancel_trip(request, trip_id):
    trip = Trip.objects.get(pk=trip_id)
    if trip.driver != request.user:
        raise PermissionDenied
    trip.status = 'X'
    trip.save()
    return redirect('rides:driver_dashboard')

@login_required
def complete_trip(request, trip_id):
    trip = Trip.objects.get(id=trip_id, driver=request.user)
    if trip.driver != request.user:
        raise PermissionDenied
        
    accepted_offers = trip.offers.filter(status='A')
    
    for offer in accepted_offers:
        if offer.carpool_request.passenger.wallet_balance < offer.fare:
            return redirect('rides:driver_dashboard')
            
    for offer in accepted_offers:
        passenger = offer.carpool_request.passenger
        driver = trip.driver
        fare = offer.fare
        
        passenger.wallet_balance -= fare
        passenger.save()
        Transaction.objects.create(user=passenger, amount=-fare, transaction_type='fare', trip=trip)
        
        driver.wallet_balance += fare
        driver.save()
        Transaction.objects.create(user=driver, amount=fare, transaction_type='earning', trip=trip)

    trip.status = 'C'
    trip.save()
    return redirect('rides:driver_dashboard')

@login_required
@api_view(['POST'])
def update_current_node(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    node_id = request.data.get('node_id')
    try:
        node = Node.objects.get(id=node_id)
    except Node.DoesNotExist:
        return Response({'error': 'Node not found'}, status=status.HTTP_404_NOT_FOUND)
    
    route_node = trip.route.filter(node=node).first()
    if not route_node:
        return Response({'error': 'Node not on route'}, status=status.HTTP_400_BAD_REQUEST)
    
    trip.route.filter(order__lte=route_node.order).update(passed=True)
    trip.current_node = node
    trip.save()
    
    return Response({'success': f'Current node updated to {node.name}'})

def create_carpool_request(request):
    if not request.user.is_passenger:
        raise PermissionDenied
    if request.method == 'POST':
        form = CarpoolRequestForm(request.POST)
        if form.is_valid():
            pickup_node = form.cleaned_data['pickup_node']
            dropoff_node = form.cleaned_data['dropoff_node']
            CarpoolRequest.objects.create(
                passenger=request.user,
                pickup_node=pickup_node,
                dropoff_node=dropoff_node,
            )
            return redirect('rides:passenger_dashboard')
    else:
        form = CarpoolRequestForm()
    return render(request, 'rides/carpool_request.html', {'form': form})

@login_required
@api_view(['POST'])
def get_carpool_requests(request, trip_id):
    if not request.user.is_driver:
        raise PermissionDenied
    try:
        trip = Trip.objects.get(pk = trip_id, driver = request.user)
    except:
        return Response({'error': 'Trip not found'}, status = status.HTTP_404_NOT_FOUND)
    
    visible_requests = utils.get_visible_requests(trip)
    serializer = CarpoolRequestSerializer(visible_requests, many = True)
    return Response(serializer.data)

@login_required
def view_carpool_requests(request, trip_id):
    if not request.user.is_driver:
        raise PermissionDenied
    
    try:
        trip = Trip.objects.get(pk = trip_id)
        visible_requests = utils.get_visible_requests(trip)
        for req in visible_requests:
            detour, fare, _, _ = utils.calculate_fare(trip, req.pickup_node, req.dropoff_node)
            req.detour = detour
            req.fare = fare
    except:
        return Response({'error': 'Trip not found'}, status = status.HTTP_404_NOT_FOUND)

    return render(request, 'rides/view_carpool_requests.html', context={
        'trip': trip,
        'requests': visible_requests,
    })

@login_required
def make_offer(request, trip_id, request_id):
    if not request.user.is_driver:
        raise PermissionDenied
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        raise PermissionDenied
    try:
        carpool_request = CarpoolRequest.objects.get(id=request_id)
    except CarpoolRequest.DoesNotExist:
        raise PermissionDenied
    
    detour, fare, pickup_order, dropoff_order = utils.calculate_fare(trip, carpool_request.pickup_node, carpool_request.dropoff_node)
    
    Offer.objects.create(
        trip=trip,
        carpool_request=carpool_request,
        detour=detour,
        fare=fare,
        pickup_order=pickup_order,
        dropoff_order=dropoff_order
    )
    return redirect('rides:view_carpool_requests', trip_id=trip_id)

@login_required
def view_offers(request, request_id):
    if not request.user.is_passenger:
        raise PermissionDenied
    try:
        carpool_request = CarpoolRequest.objects.get(id=request_id, passenger=request.user)
    except:
        return Response({'error': 'Trip not found'}, status = status.HTTP_404_NOT_FOUND)
    
    offers = carpool_request.offers.all()
    return render(request, 'rides/view_offers.html', {
        'carpool_request': carpool_request,
        'offers': offers
    })

@login_required
def confirm_offer(request, offer_id):
    if not request.user.is_passenger:
        raise PermissionDenied
    try:
        offer = Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        raise PermissionDenied
    
    if offer.carpool_request.passenger != request.user:
        raise PermissionDenied
    
    offer.status = 'A'
    offer.save()
    
    offer.carpool_request.offers.exclude(id=offer.id).update(status='R')
    
    offer.carpool_request.status = 'C'
    offer.carpool_request.save()
    
    return redirect('rides:passenger_dashboard')

@login_required
def cancel_request(request, request_id):
    if not request.user.is_passenger:
        raise PermissionDenied
    try:
        carpool_request = CarpoolRequest.objects.get(id=request_id, passenger=request.user)
    except CarpoolRequest.DoesNotExist:
        raise PermissionDenied
    
    if carpool_request.status == 'C':
        raise PermissionDenied  # cant cancel already confirmed request
    
    carpool_request.status = 'X'
    carpool_request.save()
    
    return redirect('rides:passenger_dashboard')
    