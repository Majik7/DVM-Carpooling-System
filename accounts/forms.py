from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('driver', 'Driver'),
        ('passenger', 'Passenger'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        user.is_driver = role == 'driver'
        user.is_passenger = role == 'passenger'
        if commit:
            user.save()
        return user