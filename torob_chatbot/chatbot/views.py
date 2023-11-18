from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser, Conversation, Chatbot, Message
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .services import generate_conversation_title, generate_chatbot_response, regenerate_chatbot_response


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_confirm = form.cleaned_data['password_confirm']

            if password == password_confirm:
                CustomUser.objects.create_user(username=email, email=email, password=password,
                                               user_type="regular")

                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('home')
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        form = RegistrationForm()

    return render(request, 'user/register.html', {'form': form})


@csrf_exempt
def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid login credentials.')

    return render(request, 'user/login.html', {'form': form})


@csrf_exempt
@login_required()
def chatbot_list(request):
    chatbots = Chatbot.objects.all().order_by("created_date")
    return render(request, 'chatbot/chatbot-list.html', {'chatbots': chatbots})


@csrf_exempt
@login_required()
def start_conversation(request):
    if request.method == 'POST':
        chatbot_id = request.POST.get('chatbot_id')
        chatbot = Chatbot.objects.get(id=chatbot_id)
        user = request.user
        conversation = Conversation.objects.create(chatbot=chatbot, user=user)

        return redirect('chat_details', conversation_id=conversation.id)

    chatbots = Chatbot.objects.all()
    return render(request, 'chatbot/chatbot-list.html', {'chatbots': chatbots})


@csrf_exempt
@login_required()
def chat_details(request, conversation_id):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.message_set.all()

    return render(request, 'chatbot/chat-details.html', {'conversation': conversation, 'messages': messages})


@csrf_exempt
@login_required()
def chat_history(request):
    user = request.user
    conversations = Conversation.objects.filter(user=user).order_by('-last_message_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(conversations, 5)
    try:
        conversations = paginator.page(page)
    except PageNotAnInteger:
        conversations = paginator.page(1)
    except EmptyPage:
        conversations = paginator.page(paginator.num_pages)

    return render(request, 'chatbot/chat-list.html', {'conversations': conversations})


@csrf_exempt
@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        content = request.POST.get('content', '')

        if content:

            conversation = Conversation.objects.get(pk=conversation_id)

            is_first_message = not conversation.message_set.exists()

            user_message = Message.objects.create(conversation=conversation, content=content, is_bot=False)

            bot_response = generate_chatbot_response(conversation)

            Message.objects.create(conversation=conversation, content=bot_response, is_bot=True)

            if is_first_message:
                conversation.title = generate_conversation_title(user_message.content)

            conversation.last_message_date = timezone.now()
            conversation.save()

            return redirect('chat_details', conversation_id=conversation_id)
        else:
            messages.error(request, 'Message cannot be empty.')

    return redirect('chat_history')


@require_POST
@login_required()
@csrf_exempt
def like_dislike_message(request, message_id, action):
    try:
        message = Message.objects.get(pk=message_id)
        conversation = message.conversation

        if action == 'like':
            message.likes += 1
            conversation.chatbot.likes += 1
        elif action == 'dislike':
            regenerated_content = regenerate_chatbot_response(conversation, message)
            message.original_content = message.content
            message.content = regenerated_content
            message.dislikes += 1
            conversation.chatbot.dislikes += 1

        message.save()

        conversation.chatbot.save()

        return redirect('chat_details', conversation_id=conversation.id)

    except Message.DoesNotExist:
        return HttpResponseBadRequest('Invalid message ID')


@csrf_exempt
def home(request):
    return render(request, 'home.html')
