import argparse
import json

from chatbot.models import Chatbot, ChatbotContent
from chatbot.services import embedding


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


add_embedded_docs_to_chatbot(7, "../data/data2.jsonl")
