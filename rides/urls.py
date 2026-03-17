from django.urls import path
from . import views

app_name = "rides"

urlpatterns = [
    path("passenger/dashboard", views.passenger_dashboard, name="passenger_dashboard"),
    path("driver/dashboard", views.driver_dashboard, name="driver_dashboard"),
    path("newride", views.new_ride, name="new_trip"),
    path('cancel/<int:trip_id>/', views.cancel_trip, name='cancel_trip'),
    path('trip/<int:trip_id>/complete/', views.complete_trip, name='complete_trip'),
    path('trip/<int:trip_id>/update_node/', views.update_current_node, name='update_node'),
]