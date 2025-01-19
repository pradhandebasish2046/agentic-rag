from groq import Groq
import os
from dotenv import load_dotenv

def llm_call(messages):
    client = Groq(api_key=os.getenv("groq_api_key"))
    chat_completion = client.chat.completions.create(
    messages=messages,
    model="llama-3.3-70b-versatile",
    temperature=0.2
    )
    return chat_completion.choices[0].message.content