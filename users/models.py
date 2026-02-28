from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """Custom user model supporting both roles and a wallet."""
    is_driver = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username