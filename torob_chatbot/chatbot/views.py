from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser, Conversation, Chatbot, Message
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
                return redirect('home')  # Replace 'home' with the actual URL name for your home page
            else:
                messages.error(request, 'Invalid login credentials.')

    return render(request, 'user/login.html', {'form': form})


@csrf_exempt
@login_required()
def chatbot_list(request):
    chatbots = Chatbot.objects.all()
    return render(request, 'chatbot-list.html', {'chatbots': chatbots})


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
    return render(request, 'chatbot-list.html', {'chatbots': chatbots})


@csrf_exempt
@login_required()
def chat_details(request, conversation_id):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.message_set.all()

    return render(request, 'chat-details.html', {'conversation': conversation, 'messages': messages})


@csrf_exempt
@login_required()
def chat_history(request):
    user = request.user
    conversations = Conversation.objects.filter(user=user)

    page = request.GET.get('page', 1)
    paginator = Paginator(conversations, 5)
    try:
        conversations = paginator.page(page)
    except PageNotAnInteger:
        conversations = paginator.page(1)
    except EmptyPage:
        conversations = paginator.page(paginator.num_pages)

    return render(request, 'chat-list.html', {'conversations': conversations})


@csrf_exempt
@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        content = request.POST.get('content', '')

        if content:
            conversation = Conversation.objects.get(pk=conversation_id)
            user = request.user
            message = Message.objects.create(conversation=conversation, user=user, content=content)
            return redirect('chat_details', conversation_id=conversation_id)

        else:
            messages.error(request, 'Message cannot be empty.')

    return redirect('chat_history')



@csrf_exempt
def home(request):
    return render(request, 'home.html')
