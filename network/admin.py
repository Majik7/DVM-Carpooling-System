from django.contrib import admin
from .models import Node, Edge, ServiceStatus

# Register your models here.
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(ServiceStatus)