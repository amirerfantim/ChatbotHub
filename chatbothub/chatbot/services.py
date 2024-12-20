import os

from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.db.models import Prefetch, F
from openai import OpenAI
import json
from dotenv import load_dotenv
from pgvector.django import CosineDistance, L2Distance, MaxInnerProduct
import time

from chatbot.models import Chatbot, ChatbotContent, Message

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_KEY'], base_url=os.environ['OPENAI_BASEURL'])


def generate_chatbot_response(conversation, message, max_retries=10, sleep=2):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
        {"role": "system",
         "content": "Answer the question as truthfully as possible, and if you're unsure of the answer, say \"Sorry, "
                    "I don't know\""},
    ]

    previous_messages = conversation.message_set.filter(timestamp__lt=message.timestamp)

    for previous_message in previous_messages:
        role = previous_message.role
        if role == "context" or role == "assistant":
            messages.append({"role": "assistant", "content": previous_message.content})
        else:
            messages.append({"role": role, "content": previous_message.content})

    if message.role == "user":
        messages.append({"role": "user", "content": message.content})

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.6
            )

            if not response:
                print("API response is empty.")
                time.sleep(sleep)
                continue

            content_value = response.choices[0].message.content
            return content_value

        except Exception as e:
            print(f"An error occurred: {e}")
            handle_exception(attempt, max_retries, sleep)



def generate_conversation_title(user_message_content, max_retries=5, sleep=2):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "generate a title for a conversation"},
                    {"role": "user", "content": "extract a short title from this: " + user_message_content},
                ],
                temperature=1
            )

            if not response:
                print("API response is empty.")
                time.sleep(sleep)
                continue

            content_value = response.choices[0].message.content
            return content_value

        except Exception as e:
            print(f"An error occurred: {e}")
            handle_exception(attempt, max_retries, sleep)


def embedding(message_content, max_retries=10, sleep=2):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.embeddings.create(
                input=message_content,
                model="text-embedding-ada-002",
                encoding_format='float'
            )

            if not response:
                print("API response is empty.")
                time.sleep(sleep)
                continue

            content_value = response.data[0].embedding
            return content_value


        except Exception as e:
            print(f"An error occurred: {e}")
            handle_exception(attempt, max_retries, sleep)


def handle_exception(attempt, max_retries, sleep):
    if attempt < max_retries:
        print(f"Retrying (attempt {attempt}/{max_retries})...")
    else:
        print(f"Max retries reached. Failed to get embedding.")
        return "The API is not working, try again later"
    time.sleep(sleep)


def get_relevant_context(conversation, user_message):
    user_message_embedding = embedding(user_message.content)
    chatbot_contents = ChatbotContent.objects.filter(chatbot=conversation.chatbot)
    ordered_chatbot_contents = chatbot_contents.order_by(L2Distance('embedding', user_message_embedding))
    relevant_content = ordered_chatbot_contents.first()
    if relevant_content is not None:
        Message.objects.create(conversation=conversation, content=relevant_content.content, role="context")


def get_messages_with_search(request, conversation):
    messages = conversation.message_set.select_related('conversation').prefetch_related(
        Prefetch('conversation__message_set', queryset=Message.objects.only('content', 'search_vector')),
    ).all()

    search_query = request.GET.get('search_query', '')

    if search_query:
        messages = messages.annotate(
            search=SearchVector('content'),
            rank=SearchRank(F('search'), SearchQuery(search_query))
        ).filter(search=SearchQuery(search_query)).order_by('-rank')

    messages = messages.order_by("timestamp")
    return messages
