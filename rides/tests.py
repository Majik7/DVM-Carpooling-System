from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardRedirectTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_unauthenticated_redirect(self):
        # Unauthenticated users should redirect to login
        response = self.client.get(reverse('rides:passenger_dashboard'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('rides:passenger_dashboard')}")
        
    def test_new_user_no_role_redirects_to_role_select(self):
        # Authenticated user with no role should redirect to role-select
        user = User.objects.create_user(username='newuser', password='password123')
        self.client.login(username='newuser', password='password123')
        
        response = self.client.get(reverse('rides:passenger_dashboard'))
        self.assertRedirects(response, reverse('accounts:role_select'))
        
        response = self.client.get(reverse('rides:driver_dashboard'))
        self.assertRedirects(response, reverse('accounts:role_select'))

    def test_passenger_access(self):
        # Passenger should access passenger dashboard and get 403 on driver dashboard
        user = User.objects.create_user(username='passenger', password='password123', is_passenger=True)
        self.client.login(username='passenger', password='password123')
        
        response = self.client.get(reverse('rides:passenger_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('rides:driver_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_driver_access(self):
        # Driver should access driver dashboard and redirect to driver dashboard from passenger dashboard
        user = User.objects.create_user(username='driver', password='password123', is_driver=True)
        self.client.login(username='driver', password='password123')
        
        response = self.client.get(reverse('rides:driver_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('rides:passenger_dashboard'))
        self.assertRedirects(response, reverse('rides:driver_dashboard'))
