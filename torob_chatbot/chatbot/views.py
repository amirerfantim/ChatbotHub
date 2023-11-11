from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
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

    return render(request, 'user/register.html', {'form': form})


@csrf_exempt
def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('home')  # Replace 'home' with the actual URL name for your home page
            else:
                messages.error(request, 'Invalid login credentials.')

    return render(request, 'user/login.html', {'form': form})


@csrf_exempt
def home(request):
    return render(request, 'home.html')
