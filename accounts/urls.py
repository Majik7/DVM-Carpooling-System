from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('login/driver/', views.driver_login, name='driver_login'),
    path('login/passenger/', views.passenger_login, name='passenger_login'),
    path("signup/", views.signup, name="signup"),
    path("role-select/", views.role_select, name="role_select"),
    path("wallet/", views.wallet, name="wallet"),
    path("profile/<int:user_id>", views.user_profile, name="user_profile"),
    path("ratedriver/trip/<int:trip_id>", views.rate_driver, name="rate_driver"),
    path("ratepassengers/trip/<int:trip_id>", views.rate_passengers, name="rate_passengers"),
]