import os

from dotenv import load_dotenv
from openai import OpenAI

def chat_gpt_api(labels: list):
    load_dotenv()
    # create a string from list of labels
    labels_str = ', '.join(labels)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Give me recipe with ingredients {labels_str}. Just description of steps.",
            }
        ],
        model="gpt-4o-mini",
    )
    return chat_completion.choices[0].message.content