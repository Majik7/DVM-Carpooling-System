from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from decimal import Decimal
from .models import Transaction

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

@login_required
def role_select(request):
    user = request.user
    if user.is_driver:
        return redirect('rides:driver_dashboard')
    elif user.is_passenger:
        return redirect('rides:passenger_dashboard')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'driver':
            user.is_driver = True
            user.save()
            return redirect('rides:driver_dashboard')
        elif role == 'passenger':
            user.is_passenger = True
            user.save()
            return redirect('rides:passenger_dashboard')
            
    return render(request, 'accounts/role_select.html')

@login_required
def wallet(request):
    user = request.user
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        if amount > 0:
            user.wallet_balance += Decimal(str(amount))
            user.save()
            Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='topup'
            )
            return redirect('accounts:wallet')
            
    transactions = user.transactions.all().order_by('-created_at')
    return render(request, 'accounts/wallet.html', {'transactions': transactions})