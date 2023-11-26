from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Sum
from pgvector.django import VectorField


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )


class Chatbot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    custom_prompt = models.TextField(default="You are a helpful assistant.")
    is_active = models.BooleanField(default=True)
    bot_photo = models.ImageField(upload_to='data/', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def calculate_likes_dislikes(self):
        likes_dislikes_aggregated = self.conversation_set.all().aggregate(
            total_likes=Sum('message__likes'),
            total_dislikes=Sum('message__dislikes')
        )

        total_likes = likes_dislikes_aggregated['total_likes'] or 0
        total_dislikes = likes_dislikes_aggregated['total_dislikes'] or 0

        return total_likes, total_dislikes


class ChatbotContent(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    embedding = VectorField(null=True, blank=True, dimensions=1536)


class Conversation(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    title = models.TextField(max_length=100)
    last_message_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.title = f"Chat with {self.chatbot.name}"
        super().save(*args, **kwargs)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    search_vector = SearchVectorField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    role = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    original_content = models.TextField(blank=True, null=True)
    show_original = models.BooleanField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.conversation.last_message_date = self.timestamp
        self.search_vector = SearchVector('content')
        Message.objects.filter(pk=self.pk).update(search_vector=self.search_vector)
