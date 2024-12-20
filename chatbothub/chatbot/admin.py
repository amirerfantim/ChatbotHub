from django.contrib import admin
from django.core.exceptions import PermissionDenied
from chatbot.models import CustomUser, Chatbot, ChatbotContent, Message, Conversation
from chatbot.services import embedding


class ChatbotAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'description', 'custom_prompt', 'user', 'is_active', 'bot_photo',
        'created_date', 'get_total_likes_dislikes'
    )

    list_display_links = None
    search_fields = ('name', 'description', 'user__username', 'is_active')
    list_editable = ('description', 'name', 'is_active', 'custom_prompt', 'bot_photo')
    list_editable_links = None


    def get_total_likes_dislikes(self, obj):
        total_likes, total_dislikes = obj.calculate_likes_dislikes()
        return f'👍: {total_likes}, 👎: {total_dislikes}'

    get_total_likes_dislikes.short_description = 'Likes/Dislikes'

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


class ChatbotContentAdmin(admin.ModelAdmin):
    list_display = ('get_chatbot_name', 'content', 'embedding')
    search_fields = ('chatbot__name', 'content')

    def get_chatbot_name(self, obj):
        return obj.chatbot.name

    get_chatbot_name.short_description = 'Chatbot'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(
                name='torob-admin').exists():
            return qs
        elif request.user.groups.filter(name='chatbot-admin').exists():
            return qs.filter(chatbot__user=request.user)
        else:
            return qs.none()

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser or request.user.groups.filter(name='torob-admin').exists():
            obj.embedding = embedding(obj.content)
            super().save_model(request, obj, form, change)
        elif request.user.groups.filter(name='chatbot-admin').exists():
            if obj.chatbot.user == request.user:
                obj.embedding = embedding(obj.content)
                super().save_model(request, obj, form, change)
            else:
                raise PermissionDenied("You can only add/edit content for your own chatbots.")
        else:
            raise PermissionDenied("You do not have the required permissions to add/edit content.")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.groups.filter(name='chatbot-admin').exists():
            form.base_fields['chatbot'].queryset = form.base_fields['chatbot'].queryset.filter(user=request.user)
        return form


admin.site.register(ChatbotContent, ChatbotContentAdmin)
admin.site.register(Chatbot, ChatbotAdmin)
admin.site.register(CustomUser)
admin.site.register(Message)
admin.site.register(Conversation)
