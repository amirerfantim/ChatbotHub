import json
import time

from pgvector.django import MaxInnerProduct

from chatbot.models import Chatbot, ChatbotContent
from chatbot.services import embedding


def test_dataset(chatbot_id, jsonl_file_path):
    chatbot = Chatbot.objects.get(id=chatbot_id)

    with open(jsonl_file_path, "r", encoding="utf-8") as file:
        i = 1
        count = 0
        for line in file:
            data = json.loads(line)

            doc_content = data.get("doc", "")
            question_content = data.get("question", "")

            user_message_embedding = embedding(question_content, max_retries=25, sleep=5)

            chatbot_contents = ChatbotContent.objects.filter(chatbot=chatbot)

            ordered_chatbot_contents = chatbot_contents.order_by(MaxInnerProduct('embedding', user_message_embedding))

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


test_dataset(15, "data/data.jsonl")
