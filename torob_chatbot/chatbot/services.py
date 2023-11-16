from openai import OpenAI
import json

def generate_chatbot_response(conversation):
    client = OpenAI(api_key="ENlX4UYxAfdvcCjxfITO76eIZ5Ee8NUi", base_url="https://openai.torob.ir/v1")

    # Extracting conversation context
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
