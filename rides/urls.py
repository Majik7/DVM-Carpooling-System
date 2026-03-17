from django.urls import path
from . import views

app_name = "rides"

urlpatterns = [
    path("passenger/dashboard", views.passenger_dashboard, name="passenger_dashboard"),
    path("driver/dashboard", views.driver_dashboard, name="driver_dashboard"),
    path("newride", views.new_ride, name="new_trip"),
    path('cancel/<int:trip_id>/', views.cancel_trip, name='cancel_trip'),
]