from openai import OpenAI, BadRequestError
import json
import asyncio
client = OpenAI()
async def relationship_response(openai_thread_id=None, prompt=None):
    print(f"OpenAI Thread ID: {openai_thread_id}")  # Debugging line
    print(f"Prompt: {prompt}")  # Debugging line
    # If an OpenAI thread ID is provided, use it, otherwise create a new thread
    # Split the prompt into chunks of 32000 characters if necessary
    prompt_chunks = [prompt[i:i+32000] for i in range(0, len(prompt), 32000)]
    if openai_thread_id:
        thread = client.beta.threads.retrieve(openai_thread_id)
        # Append the prompt as messages to the thread
        for chunk in prompt_chunks:
            client.beta.threads.messages.create(thread.id, role="user", content=chunk)
    else:
        # Use the first chunk to create the thread
        first_chunk = prompt_chunks.pop(0)
        thread = client.beta.threads.create(messages=[{"role": "user", "content": first_chunk}])
        openai_thread_id = thread.id  # Store the new OpenAI thread ID
        # Append remaining chunks as messages to the thread
        for chunk in prompt_chunks:
            client.beta.threads.messages.create(thread.id, role="user", content=chunk)
    thread_messages = client.beta.threads.messages.list(thread.id)
    print(thread_messages.data)
    print(f"Thread: {thread}")  # Debugging line
    # Use the hard-coded assistant ID
    assistant_id = "asst_5OaNpCp04ufX09m2tVra3Yvu"
    print(f"Assistant ID: {assistant_id}")  # Debugging line
    run = client.beta.threads.runs.create(
        thread_id=openai_thread_id,
        assistant_id=assistant_id,
    )
    while run.status not in ["completed", "expired", "cancelled", "failed"]:
            await asyncio.sleep(1)  # wait for 1 second
            run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)
    if run.status == "completed":
        # Retrieve the assistant's responses
        messages = client.beta.threads.messages.list(thread_id=openai_thread_id)
        responses = [message for message in messages.data if message.role == "assistant"]
    else:
        print(f"Run ended with status: {run.status}")
        responses = []

    print(f"Responses: {responses}")  # Debugging line

    return responses