from django.urls import path
from .views import register, home, login_view, chatbot_list

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('chatbots/', chatbot_list, name='chatbot-list'),
]
