from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_confirm = form.cleaned_data['password_confirm']

            if password == password_confirm:
                CustomUser.objects.create_user(username=email, email=email, password=password,
                                               user_type="regular")

                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('home')
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def home(request):
    return render(request, 'home.html')
