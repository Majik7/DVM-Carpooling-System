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
    path('carpool/request/', views.create_carpool_request, name='create_carpool_request'),
    path('trip/<int:trip_id>/requests/', views.get_carpool_requests, name='get_carpool_requests'),
    path('trip/<int:trip_id>/requests/page/', views.view_carpool_requests, name='view_carpool_requests'),
    path('request/<int:request_id>/offers/', views.view_offers, name='view_offers'),
    path('request/<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    path('trip/<int:trip_id>/offer/<int:request_id>/', views.make_offer, name='make_offer'),
    path('offer/<int:offer_id>/confirm/', views.confirm_offer, name='confirm_offer'),
    path('trip/<int:trip_id>', views.trip_view, name='trip_view'),
]