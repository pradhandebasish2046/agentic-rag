import chainlit as cl
from src.final_pipeline import generate_response

@cl.on_chat_start
async def main():
    await cl.Message(content="Hello World").send()

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {generate_response(message.content)}",
    ).send()