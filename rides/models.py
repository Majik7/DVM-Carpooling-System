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