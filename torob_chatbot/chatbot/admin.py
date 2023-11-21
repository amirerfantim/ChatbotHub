from django.contrib import admin
from django.core.exceptions import PermissionDenied
from chatbot.models import CustomUser, Chatbot, ChatbotContent, Message, Conversation


class ChatbotAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'description', 'custom_prompt', 'user', 'is_active', 'bot_photo', 'likes', 'dislikes', 'created_date')
    list_display_links = None
    search_fields = ('name', 'description', 'user__username', 'is_active')
    list_editable = ('description', 'name', 'is_active', 'custom_prompt', 'bot_photo')
    list_editable_links = None
    read_only_fields = ('likes', 'dislikes')

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='chatbot-admin').exists():
            return self.read_only_fields
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='torob-admin').exists():
            return qs
        elif request.user.groups.filter(name='chatbot-admin').exists():
            return qs.filter(user=request.user)
        else:
            return qs.none()

    def save_model(self, request, obj, form, change):
        if request.user.groups.filter(name='chatbot-admin').exists():
            if obj.user == request.user:
                super().save_model(request, obj, form, change)
            else:
                raise PermissionDenied("You can only create a chatbot for yourself.")
        else:
            super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.groups.filter(name='chatbot-admin').exists():
            form.base_fields['user'].queryset = CustomUser.objects.filter(id=request.user.id)
        return form


admin.site.register(Chatbot, ChatbotAdmin)
admin.site.register(CustomUser)
admin.site.register(ChatbotContent)
admin.site.register(Message)
admin.site.register(Conversation)
