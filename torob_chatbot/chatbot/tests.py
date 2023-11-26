from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Chatbot, Conversation, Message, ChatbotContent


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


class StartConversationViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

        image_content = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\x1f'
                         b'\x15\xc4\x89\x00\x00\x00\nIDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\x15\x00\x00\x00\x00IEND'
                         b'\xaeB`\x82')
        self.image = SimpleUploadedFile("test_image.png", image_content, content_type="image/png")

        self.chatbot = Chatbot.objects.create(
            user=self.user,
            name='Test Chatbot',
            description='Test Description',
            custom_prompt='Test Prompt',
            is_active=True,
            bot_photo=self.image
        )

    def test_start_conversation_post(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('start_conversation'), {'chatbot_id': self.chatbot.id})

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Conversation.objects.count(), 1)

        conversation = Conversation.objects.first()
        self.assertEqual(conversation.chatbot, self.chatbot)
        self.assertEqual(conversation.user, self.user)

        self.assertRedirects(response, reverse('chat_details', args=[conversation.id]))

    def test_start_conversation_get(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('start_conversation'))

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context['chatbots'], Chatbot.objects.all(), transform=lambda x: x)

    def test_start_conversation_unauthenticated(self):
        response = self.client.post(reverse('start_conversation'), {'chatbot_id': self.chatbot.id})

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, reverse('login') + '?next=' + reverse('start_conversation'))


class ChatHistoryViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        image_content = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x06\x00\x00\x00\x1f'
                         b'\x15\xc4\x89\x00\x00\x00\nIDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\x15\x00\x00\x00\x00IEND'
                         b'\xaeB`\x82')
        self.image = SimpleUploadedFile("test_image.png", image_content, content_type="image/png")

        self.active_chatbot = Chatbot.objects.create(user=self.user, name='Active Chatbot', is_active=True,
                                                     bot_photo=self.image)
        self.inactive_chatbot = Chatbot.objects.create(user=self.user, name='Inactive Chatbot', is_active=False,
                                                       bot_photo=self.image)

        Conversation.objects.create(chatbot=self.active_chatbot, user=self.user, title='Conversation 1')
        Conversation.objects.create(chatbot=self.active_chatbot, user=self.user, title='Conversation 2')

    def test_user_redirected_to_login_if_not_logged_in(self):
        response = self.client.get(reverse('chat_history'))

        self.assertRedirects(response, '/login/?next=/chat-history/', status_code=302, target_status_code=200)

    def test_no_conversations_to_display(self):
        get_user_model().objects.create_user(username='noconvuser', password='testpass')

        self.client.login(username='noconvuser', password='testpass')

        response = self.client.get(reverse('chat_history'))

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context['conversations'], [])


class LikeDislikeMessageViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test_user", password="test_password")
        self.client.login(username="test_user", password="test_password")
        self.chatbot = Chatbot.objects.create(user=self.user)
        self.content = ChatbotContent.objects.create(chatbot=self.chatbot)
        self.conversation = Conversation.objects.create(chatbot=self.chatbot, user=self.user)
        self.message = Message.objects.create(conversation=self.conversation)

    def test_like_message(self):
        url = reverse('like_dislike_message', args=[self.message.id, 'like'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        updated_message = Message.objects.get(pk=self.message.id)

        self.assertEqual(updated_message.likes, 1)

    def test_dislike_message(self):
        url = reverse('like_dislike_message', args=[self.message.id, 'dislike'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        updated_message = Message.objects.get(pk=self.message.id)

        self.assertEqual(updated_message.dislikes, 1)
        self.assertNotEqual(updated_message.content, self.message.content)

    def test_invalid_message_id(self):
        url = reverse('like_dislike_message', args=[999, 'like'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid message ID')


class SwitchContentViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test_user", password="test_password")
        self.client.login(username="test_user", password="test_password")
        self.chatbot = Chatbot.objects.create(user=self.user)
        self.content = ChatbotContent.objects.create(chatbot=self.chatbot)
        self.conversation = Conversation.objects.create(chatbot=self.chatbot, user=self.user)
        self.assistant_message = Message.objects.create(conversation=self.conversation, role='assistant', dislikes=1)
        self.user_message = Message.objects.create(conversation=self.conversation, role='user')

    def test_switch_content_show_original(self):
        url = reverse('switch_content', args=[self.assistant_message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        updated_message = Message.objects.get(pk=self.assistant_message.id)

        self.assertTrue(updated_message.show_original)

    def test_switch_content_hide_original(self):
        self.assistant_message.show_original = True
        self.assistant_message.save()

        url = reverse('switch_content', args=[self.assistant_message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        updated_message = Message.objects.get(pk=self.assistant_message.id)

        self.assertFalse(updated_message.show_original)

    def test_switch_content_user_message(self):
        url = reverse('switch_content', args=[self.user_message.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        updated_user_message = Message.objects.get(pk=self.user_message.id)

        self.assertIsNone(updated_user_message.show_original)

    def test_switch_content_invalid_message_id(self):
        url = reverse('switch_content', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid message ID')
