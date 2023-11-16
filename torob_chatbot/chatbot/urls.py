from django.urls import path
from .views import register, home, login_view, chatbot_list, start_conversation, chat_details

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('chatbots/', chatbot_list, name='chatbot-list'),
    path('start-conversation/', start_conversation, name='start_conversation'),
    path('chat-details/<int:conversation_id>/', chat_details, name='chat_details'),
]
