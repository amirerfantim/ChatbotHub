import os

from django.utils import timezone
from openai import OpenAI
import json
from dotenv import load_dotenv

from chatbot.models import Message

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_KEY'], base_url=os.environ['OPENAI_BASEURL'])


def generate_chatbot_response(conversation):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
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


def regenerate_chatbot_response(conversation, message):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
    ]

    previous_messages = conversation.message_set.filter(timestamp__lt=message.timestamp)

    for previous_message in previous_messages:
        role = "user" if not previous_message.is_bot else "assistant"
        messages.append({"role": role, "content": previous_message.content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
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
