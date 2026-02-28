from django.db import models

# Create your models here.
class Ride(models.Model):
    passenger = models.ForeignKey('Passenger', on_delete=models.CASCADE) # change the cascade later
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE)