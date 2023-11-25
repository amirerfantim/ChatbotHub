import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from pgvector.django import CosineDistance, L2Distance, MaxInnerProduct
import time

from chatbot.models import Chatbot, ChatbotContent

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_KEY'], base_url=os.environ['OPENAI_BASEURL'])


def generate_chatbot_response(conversation, message, max_retries=10, sleep=2):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
        {"role": "system",
         "content": "Answer the question as truthfully as possible, and if you're unsure of the answer, say \"Sorry, I don't know\""},
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
