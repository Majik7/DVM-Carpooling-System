from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_driver = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def rating(self):
        ratings_received = self.ratings_received.all()

        if not ratings_received:
            return 0.0
        else:
            total_score = sum(i.score for i  in ratings_received)
            return round(total_score / len(ratings_received), 1)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('topup', 'Top Up'),
        ('fare', 'Fare Deduction'),
        ('earning', 'Driver Earning'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    trip = models.ForeignKey('rides.Trip', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    rater  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_given")
    ratee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_received")
    trip = models.ForeignKey('rides.Trip', on_delete=models.CASCADE) # used rides.Trip because of circular import error
    score = models.IntegerField(default=5)