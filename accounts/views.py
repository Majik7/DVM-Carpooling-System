from django.shortcuts import render, redirect
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