from django.contrib import admin
from chatbot.models import CustomUser, Chatbot, ChatbotContent, Message, Conversation, UserRating

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Chatbot)
admin.site.register(ChatbotContent)
admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(UserRating)
