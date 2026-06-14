from django.shortcuts import render, redirect, get_object_or_404
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
from network.models import Node, ServiceStatus
from .serializers import CarpoolRequestSerializer

# Create your views here.

@login_required
def passenger_dashboard(request):
    if request.user.is_driver:
        return redirect("rides:driver_dashboard")
    
    if not request.user.is_passenger:
        return redirect('accounts:role_select')
    
    active_requests = CarpoolRequest.objects.filter(passenger=request.user, status='P')
    confirmed_requests = CarpoolRequest.objects.filter(passenger=request.user, status='C').exclude(offers__trip__status = 'C')
    cancelled_requests = CarpoolRequest.objects.filter(passenger=request.user, status='X')

    completed_requests = CarpoolRequest.objects.filter(passenger=request.user, status='C', offers__trip__status='C')
    
    return render(request, 'rides/passenger_dash.html', {
        'active_requests': active_requests,
        'confirmed_requests': confirmed_requests,
        'cancelled_requests': cancelled_requests,
        'completed_requests': completed_requests,
        'passenger': request.user
    })

@login_required
def driver_dashboard(request):
    if not request.user.is_driver:
        if not request.user.is_passenger:
            return redirect('accounts:role_select')
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
    if not is_service_active():
        return render(request, 'rides/suspended.html')
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

# @login_required
# def create_carpool_request(request):
#     if not is_service_active():
#         return render(request, 'rides/suspended.html')
#     if not request.user.is_passenger:
#         raise PermissionDenied
#     if request.method == 'POST':
#         form = CarpoolRequestForm(request.POST)
#         if form.is_valid():
#             pickup_node = form.cleaned_data['pickup_node']
#             dropoff_node = form.cleaned_data['dropoff_node']
#             CarpoolRequest.objects.get_or_create(
#                 passenger=request.user,
#                 pickup_node=pickup_node,
#                 dropoff_node=dropoff_node,
#             )
#             return redirect('rides:passenger_dashboard')
#     else:
#         form = CarpoolRequestForm()
#     return render(request, 'rides/carpool_request.html', {'form': form})

@login_required
def create_carpool_request(request, trip_id):
    if not request.user.is_passenger:
        raise PermissionDenied
    
    if not is_service_active():
        return render(request, 'rides/suspended.html')
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = CarpoolRequestForm(request.POST)
        if form.is_valid():
            pickup_node = form.cleaned_data['pickup_node']
            dropoff_node = form.cleaned_data['dropoff_node']
            
            CarpoolRequest.objects.get_or_create(
                passenger=request.user,
                pickup_node=pickup_node,
                dropoff_node=dropoff_node,
                status='P',
                trip=trip,
            )
            return redirect('rides:passenger_dashboard')
    else:
        form = CarpoolRequestForm(initial={
            "pickup_node": request.GET.get("pickup_id"),
            "dropoff_node": request.GET.get("dropoff_id"),
        })
    
    return render(request, 'rides/carpool_request.html', {'form': form, 'trip': trip})

@login_required
@api_view(['GET'])
def get_carpool_requests(request, trip_id):
    if not request.user.is_driver:
        raise PermissionDenied
    try:
        trip = Trip.objects.get(pk = trip_id, driver = request.user)
    except:
        return Response({'error': 'Trip not found'}, status = status.HTTP_404_NOT_FOUND)
    
    visible_requests = trip.requests.filter(status = "P")
    serializer = CarpoolRequestSerializer(visible_requests, many = True)
    return Response(serializer.data)

@login_required
def view_carpool_requests(request, trip_id):
    if not request.user.is_driver:
        raise PermissionDenied
    
    try:
        trip = Trip.objects.get(pk=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        return redirect('rides:driver_dashboard')
    
    visible_requests = trip.requests.filter(status = "P")
    for req in visible_requests:
        detour, fare, _, _, _ = utils.calculate_fare(trip, req.pickup_node, req.dropoff_node)
        req.detour = detour
        req.fare = fare
    
    return render(request, 'rides/view_carpool_requests.html', {
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
    
    detour, fare, pickup_order, dropoff_order, _ = utils.calculate_fare(trip, carpool_request.pickup_node, carpool_request.dropoff_node)
    
    Offer.objects.get_or_create(
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
    
    trip = offer.trip
    pickup_node = offer.carpool_request.pickup_node
    dropoff_node = offer.carpool_request.dropoff_node

    # rebuilding route
    remaining = trip.route.filter(passed=False).order_by('order')
    current = remaining.first().node
    destination = remaining.last().node
    last_passed = trip.route.filter(passed=True).order_by('order').last()
    last_passed_order = last_passed.order if last_passed else 0

    topickup = utils.create_path(current, pickup_node)
    picktodrop = utils.create_path(pickup_node, dropoff_node)
    droptoend = utils.create_path(dropoff_node, destination)

    if not topickup or not picktodrop or not droptoend:
        return redirect('rides:passenger_dashboard')

    full_path = topickup + picktodrop[1:] + droptoend[1:]

    remaining.delete()
    for i, node in enumerate(full_path):
        RouteNode.objects.create(
            trip=trip,
            node=node,
            order=last_passed_order + 1 + i
        )

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
    
def is_service_active():
    status = ServiceStatus.objects.first()
    return status.is_active if status else True

@login_required
def trip_view(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    
    passenger_list = [offer.carpool_request.passenger for offer in trip.offers.filter(status='A')]
    
    route = trip.route.order_by('order')
    current_node = trip.current_node
    remaining = trip.route.filter(passed=False).order_by('order')
    
    return render(request, 'rides/trip_view.html', {
        'trip': trip,
        'passengers': passenger_list,
        'route': route,
        'current_node': current_node,
        'remaining': remaining,
    })

@login_required
def show_available_rides(request):
    if not request.user.is_passenger:
        raise PermissionDenied
    
    nodes = Node.objects.all()
    tripset = None
    
    pickup_id = request.GET.get('pickup_node_id')
    dropoff_id = request.GET.get('dropoff_node_id')
    
    if pickup_id and dropoff_id:
        try:
            pickup_node = Node.objects.get(id=pickup_id)
            dropoff_node = Node.objects.get(id=dropoff_id)
        except Node.DoesNotExist:
            return render(request, 'rides/available_rides.html', {'nodes': nodes})
        
        pickup_within2 = utils.nodes_within_2(pickup_node)
        pickup_within2.add(pickup_node)

        dropoff_within2 = utils.nodes_within_2(dropoff_node)
        dropoff_within2.add(dropoff_node)

        tripset = Trip.objects.filter(
            route__node__in = pickup_within2,
            route__passed = False,
            status = "O"
        ).filter(route__node__in = dropoff_within2).distinct()
    
    return render(request, 'rides/available_rides.html', {  # outside the if block
        'nodes': nodes,
        'trips': tripset,
        'pickup_id': pickup_id,
        'dropoff_id': dropoff_id,
    })

@login_required
def update_by_one(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        raise PermissionDenied
    
    remaining = list(trip.route.filter(passed=False).order_by('order'))
    
    if not remaining:
        return redirect('rides:trip_view', trip_id=trip_id)
    
    # if trip.current_node == trip.route.order_by('order').first().node:
    #     current = remaining[1]
    # else:
    #     current = remaining[0]
    if not trip.current_node:
        current = remaining[0]

    elif len(remaining) < 2:
        current = remaining[-1]
        trip.status = "C"
        trip.save()

    else:
        current = remaining[1]

    trip.current_node = current.node
    trip.save()
    
    trip.route.filter(order__lt=current.order).update(passed=True)

    print("current_node:", trip.current_node)
    print("remaining:", remaining)
    print("selected current:", current.node)
    
    return redirect('rides:trip_view', trip_id=trip_id)