from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from chatbot.views import register, home, login_view, chatbot_list, start_conversation, chat_details, chat_history, \
    send_message, like_dislike_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', home, name='home'),
    path('chatbots/', chatbot_list, name='chatbot-list'),
    path('start-conversation/', start_conversation, name='start_conversation'),
    path('chat-details/<int:conversation_id>/', chat_details, name='chat_details'),
    path('send-message/<int:conversation_id>/', send_message, name='send_message'),
    path('chat-history/', chat_history, name='chat_history'),
    path('like-dislike-message/<int:message_id>/<str:action>/', like_dislike_message, name='like_dislike_message'),
]
# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)