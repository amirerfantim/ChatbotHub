from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import register, home, login_view, chatbot_list, start_conversation, chat_details, chat_history

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('chatbots/', chatbot_list, name='chatbot-list'),
    path('start-conversation/', start_conversation, name='start_conversation'),
    path('chat-details/<int:conversation_id>/', chat_details, name='chat_details'),
    path('chat-history/', chat_history, name='chat_history'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
