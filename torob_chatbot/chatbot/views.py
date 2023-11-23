from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from pgvector.django import L2Distance

from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login
from .models import CustomUser, Conversation, Chatbot, Message, ChatbotContent
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .services import generate_conversation_title, generate_chatbot_response, embedding
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import SearchQuery, SearchVector
from .forms import SearchForm
from .models import Conversation
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F


@csrf_exempt
def register(request):
    error_message = None

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                password_confirm = form.cleaned_data['password_confirm']

                if password == password_confirm:
                    CustomUser.objects.create_user(username=email, email=email, password=password)

                    messages.success(request, 'Registration successful. You can now log in.')
                    return redirect('home')
                else:
                    error_message = 'Passwords do not match.'
        except IntegrityError:
            error_message = 'Email is already registered. Please choose a different email.'
        except Exception as e:
            error_message = f'An error occurred: {str(e)}'

    else:
        form = RegistrationForm()

    return render(request, 'user/register.html', {'form': form, 'error_message': error_message})


@csrf_exempt
def login_view(request):
    form = LoginForm()
    error_message = ''

    if request.method == 'POST':
        form = LoginForm(request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                user = authenticate(request, username=email, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, 'Login successful.')
                    return redirect('home')
                else:
                    error_message = 'Invalid login credentials.'
        except Exception as e:
            error_message = f'An error occurred: {str(e)}'

    return render(request, 'user/login.html', {'form': form, 'error_message': error_message})


@csrf_exempt
@login_required()
def chatbot_list(request):
    chatbots = Chatbot.objects.all().order_by("created_date").filter(is_active=True)
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
    conversation = Conversation.objects.filter(user=request.user, chatbot__is_active=True).get(id=conversation_id)
    messages = conversation.message_set.all()

    search_query = request.GET.get('search_query', '')

    if search_query:
        messages = messages.annotate(
            search=SearchVector('content'),
            rank=SearchRank(F('search'), SearchQuery(search_query))
        ).filter(search=SearchQuery(search_query)).order_by('-rank')

    for message in messages:
        message.original_content = mark_safe(message.original_content)
        message.content = mark_safe(message.content)
    return render(request, 'chatbot/chat-details.html',
                  {'conversation': conversation, 'messages': messages, 'search_query': search_query})


@csrf_exempt
@login_required()
def chat_history(request):
    user = request.user
    conversations = Conversation.objects.filter(user=user, chatbot__is_active=True).order_by('-last_message_date')

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

            user_message = Message.objects.create(conversation=conversation, content=content, role="user")

            user_message_embedding = embedding(user_message.content)

            chatbot_contents = ChatbotContent.objects.filter(chatbot=conversation.chatbot)

            ordered_chatbot_contents = chatbot_contents.order_by(L2Distance('embedding', user_message_embedding))

            relevant_contents = [content.content for content in ordered_chatbot_contents[:1]]

            if len(relevant_contents) > 0:
                Message.objects.create(conversation=conversation, content=relevant_contents[0], role="context")

            bot_response = generate_chatbot_response(conversation, user_message)

            Message.objects.create(conversation=conversation, content=bot_response, role="assistant")

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

        if action == 'like' and message.likes == 0:
            message.likes += 1
            conversation.chatbot.likes += 1
        elif action == 'dislike':
            regenerated_content = generate_chatbot_response(conversation, message)
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
@login_required()
def switch_content(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
        conversation = message.conversation

        if message.role == 'assistant' and message.dislikes > 0:
            if message.show_original:
                message.show_original = False
            else:
                message.show_original = True

            message.save()

            return redirect('chat_details', conversation_id=conversation.id)

    except Message.DoesNotExist:
        return HttpResponseBadRequest('Invalid message ID')

    return redirect('chat_details', conversation_id=conversation.id)


@csrf_exempt
def home(request):
    return render(request, 'home.html')
