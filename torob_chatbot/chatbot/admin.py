from django.contrib import admin
from chatbot.models import CustomUser, Chatbot, ChatbotContent, Message, Conversation


class ChatbotAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'user', 'is_active', 'bot_photo', 'created_date')
    list_display_links = None
    search_fields = ('name', 'description', 'user', 'is_active')
    list_editable = ('description', 'name', 'is_active', 'bot_photo')
    list_editable_links = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)


admin.site.register(Chatbot, ChatbotAdmin)
admin.site.register(CustomUser)
admin.site.register(ChatbotContent)
admin.site.register(Message)
admin.site.register(Conversation)
