from django.db import models


class User(models.Model):
    user_type_choices = [
        ('normal', 'Normal User'),
        ('chatbot_builder', 'Chatbot Builder'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=15, choices=user_type_choices, default='normal')
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)


class Chatbot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    bot_photo = models.ImageField(upload_to='chatbot_photos/', null=True, blank=True)



class ChatbotContent(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    content = models.TextField(max_length=800)


class Conversation(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class UserRating(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
