from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('regular', 'Regular user'),
        ('chatbot_creator', 'Chatbot Creator'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='regular')

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
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)


class ChatbotContent(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    content = models.TextField(max_length=800)


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

    def update_last_message_date(self):
        last_message = self.message_set.last()
        if last_message:
            self.last_message_date = last_message.timestamp
            self.save()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    original_content = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.conversation.update_last_message_date()

# class UserRating(models.Model):
#     message = models.ForeignKey(Message, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     like = models.BooleanField(default=False)
#     dislike = models.BooleanField(default=False)
