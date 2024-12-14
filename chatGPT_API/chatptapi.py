import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Give me recipe for a chocolate cake.",
        }
    ],
    model="gpt-4o-mini",
)
print(chat_completion.choices[0].message.content)