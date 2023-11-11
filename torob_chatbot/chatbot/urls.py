from django.urls import path
from .views import register, home, login_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home')
]
