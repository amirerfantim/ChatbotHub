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

    def test_home_view_unauthenticated_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
        self.assertIn('is_auth', response.context)
        self.assertFalse(response.context['is_auth'])


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

    def test_start_conversation_view(self):
        self.client.login(username='test@example.com', password='testpassword')

        response = self.client.post('/start-conversation/', {'chatbot_id': self.chatbot.id})
        self.assertEqual(response.status_code, 302)

    def test_send_empty_message(self):
        self.client.login(username='test@example.com', password='testpassword')

        initial_message_count = Message.objects.filter(conversation=self.conversation).count()

        response = self.client.post(reverse('send_message', args=[self.conversation.id]), {'content': ''})
        self.assertEqual(response.status_code, 302)

        updated_message_count = Message.objects.filter(conversation=self.conversation).count()

        self.assertEqual(updated_message_count, initial_message_count)


class SendMessageViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

        self.chatbot = Chatbot.objects.create(user=self.user, name='Test Chatbot', description='Test Description')

        self.conversation = Conversation.objects.create(chatbot=self.chatbot, user=self.user)

    def test_send_message_view(self):
        self.client.force_login(self.user)

        initial_message_count = Message.objects.filter(conversation=self.conversation).count()

        response = self.client.post(reverse('send_message', args=[self.conversation.id]), {'content': 'Test message'})
        self.assertEqual(response.status_code, 302)

        updated_message_count = Message.objects.filter(conversation=self.conversation).count()

        self.assertEqual(updated_message_count, initial_message_count + 2)
