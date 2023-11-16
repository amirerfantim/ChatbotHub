from openai import OpenAI
import json


def generate_chatbot_response(user_message):
    client = OpenAI(api_key="ENlX4UYxAfdvcCjxfITO76eIZ5Ee8NUi", base_url="https://openai.torob.ir/v1")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ]
    )

    json_str = json.loads(response)
    content_value = json_str['choices'][0]['message']['content']
    return content_value
