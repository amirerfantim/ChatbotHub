# chatbot/services.py
from django.utils import timezone
from openai import OpenAI
import json

from chatbot.models import Message

client = OpenAI(api_key="ENlX4UYxAfdvcCjxfITO76eIZ5Ee8NUi", base_url="https://openai.torob.ir/v1")


def generate_chatbot_response(conversation):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]

    for message in conversation.message_set.all():
        role = "user" if not message.is_bot else "assistant"
        messages.append({"role": role, "content": message.content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value


def regenerate_chatbot_response(message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "regenerate a message"},
            {"role": "user", "content": message.content},
        ]
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value


def generate_conversation_title(user_message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "generate a title for a conversation"},
            {"role": "user", "content": "extract a short title from this: " + user_message},
        ]
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value
