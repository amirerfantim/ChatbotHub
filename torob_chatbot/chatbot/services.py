import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from pgvector.django import VectorField

from chatbot.models import Chatbot, ChatbotContent

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_KEY'], base_url=os.environ['OPENAI_BASEURL'])


def generate_chatbot_response(conversation, message):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
    ]

    previous_messages = conversation.message_set.filter(timestamp__lt=message.timestamp)

    for previous_message in previous_messages:
        role = message.role
        messages.append({"role": role, "content": previous_message.content})

    if message.role == "user":
        messages.append({"role": "user", "content": message.content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value


def generate_conversation_title(user_message_content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "generate a title for a conversation"},
            {"role": "user", "content": "extract a short title from this: " + user_message_content},
        ]
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value


def embedding(message_content):
    response = client.embeddings.create(
        input=message_content,
        model="text-embedding-ada-002",
        encoding_format='float'
    )

    json_str = json.loads(response)
    content_value = json_str['data'][0]['embedding']
    return content_value



def add_embedded_docs_to_chatbot(chatbot_id, jsonl_file_path):
    chatbot = Chatbot.objects.get(id=chatbot_id)

    with open(jsonl_file_path, "r", encoding="utf-8") as file:
        i = 1
        for line in file:
            data = json.loads(line)

            doc_content = data.get("doc", "")

            chatbot_content_instance = ChatbotContent.objects.create(
                chatbot=chatbot,
                content=doc_content,
                embedding=embedding(doc_content)
            )


            chatbot_content_instance.save()
            print(str(i) + ' -> ' + doc_content + '\n')
            i += 1


