from django.contrib import admin
from .models import Trip, Offer, CarpoolRequest

# Register your models here.
admin.site.register(Trip)
admin.site.register(Offer)
admin.site.register(CarpoolRequest)