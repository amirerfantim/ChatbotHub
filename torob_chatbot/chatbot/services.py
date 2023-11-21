import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from pgvector.django import CosineDistance, L2Distance
import time

from chatbot.models import Chatbot, ChatbotContent

load_dotenv()
client = OpenAI(api_key=os.environ['OPENAI_KEY'], base_url=os.environ['OPENAI_BASEURL'])


def generate_chatbot_response(conversation, message, max_retries=5, sleep=2):
    messages = [
        {"role": "system", "content": conversation.chatbot.custom_prompt},
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
                messages=messages
            )

            if not response:
                print("API response is empty.")
                time.sleep(sleep)
                continue

            json_str = json.loads(response)
            content_value = json_str['choices'][0]['message']['content']
            return content_value

        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries:
                print(f"Retrying (attempt {attempt + 1}/{max_retries})...")
            else:
                print(f"Max retries reached. Failed to get embedding.")
                return "The API is not working, try again later"
            time.sleep(sleep)


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

            content_value = response['data'][0]['embedding']
            return content_value


        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries:
                print(f"Retrying (attempt {attempt + 1}/{max_retries})...")
            else:
                print(f"Max retries reached. Failed to get embedding.")
                return "The API is not working, try again later"
            time.sleep(sleep)


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


def test_dataset(chatbot_id, jsonl_file_path):
    chatbot = Chatbot.objects.get(id=chatbot_id)

    with open(jsonl_file_path, "r", encoding="utf-8") as file:
        i = 1
        count = 0
        for line in file:
            data = json.loads(line)

            doc_content = data.get("doc", "")
            question_content = data.get("question", "")

            max_retries = 20
            retry_delay = 3

            for _ in range(max_retries):
                try:
                    user_message_embedding = embedding(question_content)
                    break
                except Exception as e:
                    print(f"An exception occurred  -> Retrying.....: {e}\n")
                    time.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to get user_message_embedding.")

            chatbot_contents = ChatbotContent.objects.filter(chatbot=chatbot)

            ordered_chatbot_contents = chatbot_contents.order_by(L2Distance('embedding', user_message_embedding))

            most_relevant_content = ordered_chatbot_contents.first().content

            print("******************\n")

            if doc_content == most_relevant_content:
                count += 1
                print(str(i), " was success, success count so far:  ", str(count), "\n")
            else:
                print(str(i), " was fail, success count so far: ", str(count) + "\n")
                print("retrieved doc: ", most_relevant_content, '\n')
                print("original doc: ", doc_content, '\n')
                print()
            print("******************\n")
            i += 1
        print("similarity: ", count / i)
