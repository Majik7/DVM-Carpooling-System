from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import SignupForm

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            role = request.POST.get('role')
            user.is_driver = (role == 'driver')
            user.is_passenger = (role == 'passenger')
            user.save()
            
            return redirect('accounts:login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def driver_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_driver:
                form.add_error(None, 'This account is not registered as a driver.')
            else:
                login(request, user)
                return redirect('rides:driver_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/driver_login.html', {'form': form})

def passenger_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_passenger:
                form.add_error(None, 'This account is not registered as a passenger.')
            else:
                login(request, user)
                return redirect('rides:passenger_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/passenger_login.html', {'form': form})