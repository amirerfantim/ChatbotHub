from django.contrib import admin
from chatbot.models import CustomUser, Chatbot, ChatbotContent, Message, Conversation

admin.site.register(Chatbot)
admin.site.register(CustomUser)
admin.site.register(ChatbotContent)
admin.site.register(Message)
admin.site.register(Conversation)
