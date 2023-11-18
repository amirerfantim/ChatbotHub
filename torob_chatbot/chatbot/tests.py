from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Chatbot, Conversation, Message


class ChatbotViewsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

        self.chatbot = Chatbot.objects.create(user=self.user, name='Test Chatbot', description='Test Description')

    def test_register_view(self):
        response = self.client.post('/register/', {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_view(self):
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_chatbot_list_view(self):
        self.client.login(username='test@example.com', password='testpassword')

        response = self.client.get('/chatbots/')
        self.assertEqual(response.status_code, 302)



class ChatDetailsViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

        self.chatbot = Chatbot.objects.create(user=self.user, name='Test Chatbot', description='Test Description')

        self.conversation = Conversation.objects.create(chatbot=self.chatbot, user=self.user)

    def test_chat_details_view(self):
        self.client.login(username='test@example.com', password='testpassword')

        response = self.client.get(f'/chat-details/{self.conversation.id}/')
        self.assertEqual(response.status_code, 302)


