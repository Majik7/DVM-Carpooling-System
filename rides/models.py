from django.db import models
from accounts.models import User
from network.models import Node

class Trip(models.Model):
    STATUS_CHOICES = [
        ('O', 'Ongoing'),
        ('C', 'Completed'),
        ('X', 'Cancelled'),
    ]
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    start_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='trip_starts')
    end_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='trip_ends')
    current_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='trip_currents', null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='O', max_length=1)
    max_passengers = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class RouteNode(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='route')
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    order = models.IntegerField()
    passed = models.BooleanField(default=False)

class CarpoolRequest(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('X', 'Cancelled'),
    ]
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carpool_requests')
    pickup_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='pickups')
    dropoff_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='dropoffs')
    status = models.CharField(choices=STATUS_CHOICES, default='P', max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Offer(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    ]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='offers')
    carpool_request = models.ForeignKey(CarpoolRequest, on_delete=models.CASCADE, related_name='offers')
    detour = models.IntegerField(default=0)
    fare = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(choices=STATUS_CHOICES, default='P', max_length=1)
    pickup_order = models.IntegerField(default=0)
    dropoff_order = models.IntegerField(default=0)