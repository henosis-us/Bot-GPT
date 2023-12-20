# openai_utils.py
import json
from urlfetch import urlFetch
from openai import OpenAI, BadRequestError
from pplxapi import pplxresponse
import asyncio
client = OpenAI()
from .tokenizer import num_tokens_from_string, num_tokens_from_messages
from youtube_transcript_grabber import get_transcript
async def fetch_and_prepare_content_for_lm_tool(url):
    try:
        # Since the original function is synchronous, use asyncio to run it in an executor
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, urlFetch, url)
        return content
    except Exception as e:
        print(f"An error occurred while fetching content: {e}")
        return None
async def assistant_response(openai_thread_id=None, prompt=None):
    print(f"OpenAI Thread ID: {openai_thread_id}")  # Debugging line
    # If an OpenAI thread ID is provided, use it, otherwise create a new thread
    if openai_thread_id:
        thread = client.beta.threads.retrieve(openai_thread_id)
    else:
        # Split the prompt into chunks of 32000 characters if necessary
        prompt_chunks = [prompt[i:i+32000] for i in range(0, len(prompt), 32000)]
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
    assistant_id = "asst_z9ChMmBNvr3FucVrXZFZ6vpl"
    print(f"Assistant ID: {assistant_id}")  # Debugging line
    run = client.beta.threads.runs.create(
        thread_id=openai_thread_id,
        assistant_id=assistant_id,
    )
    # Wait for the run to reach a final state
    while run.status not in ["completed", "expired", "cancelled", "failed"]:
        await asyncio.sleep(1)  # wait for 1 second
        run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)  # refresh the run object

        # Check if the run requires action
        if run.status == "requires_action":
            tool_outputs = []  # Initialize an empty list to collect tool outputs
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                output = None
                if function_name == "urlFetch":
                    print("calling fetch content")
                    url = arguments["url"]
                    output = urlFetch(url)
                    if output:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output,
                        })
                    else:
                        print("ALERT NO CONTENT: urlFetch returned None or error message.")
                if function_name == "query_llm_internet":
                    print("calling internet search")
                    query = arguments["query"]
                    print(query)
                    try:
                        output = await pplxresponse(query)
                        if output:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": output,
                            })
                        else:
                            print("ALERT NO LLM OUTPUT: pplxresponse returned None or empty string.")
                    except Exception as e:
                        print(f"An error occurred while awaiting pplxresponse: {e}")
                if function_name == "generate_image":
                    print("calling image creation")
                    image_url = await generate_image(arguments["prompt"], arguments["quality"])
                    if image_url:
                        # Submit the image URL as a tool output
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": image_url,
                        })
                        print(f"Image URL: {image_url}")
                    else:
                        print("ALERT NO IMAGE: generate_image returned None or empty string.")
                if function_name == "get_transcript":
                    print("calling video transcript search")
                    output = await get_transcript(arguments["youtube_url"])
                    # If the transcript is too long, call gpt-4 to summarize it with context from the original prompt
                    if len(output) > 32000:
                        summary = client.chat.completions.create(
                            model="gpt-4-1106-preview",
                            messages=[{"role": "system", "content": """As a professional summarizer, create a concise and comprehensive summary of the provided text, be it an article, post, conversation, or passage, while adhering to these guidelines:

Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.

Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects.

Rely strictly on the provided text, without including external information.

Format the summary in paragraph form for easy understanding.

Conclude your notes with [End of Notes, Message #X] to indicate completion, where "X" represents the total number of messages that I have sent. In other words, include a message counter where you start with #1 and add 1 to the message counter every time I send a message.

By following this optimized prompt, you will generate an effective summary that encapsulates the essence of the given text in a clear, concise, and reader-friendly manner."""}, 
                                      {"role": "user", "content": output}],
                            max_tokens=4000,
                            temperature=.3,
                            top_p=.3
                        )
                        output = summary.choices[0].message.content
                    print(output)
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output,
                    })
                    # Submit the output as a tool output
            if tool_outputs:
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )    
    # Check the final status of the run
    if run.status == "completed":
        # Retrieve the assistant's responses
        messages = client.beta.threads.messages.list(thread_id=openai_thread_id)
        responses = [message for message in messages.data if message.role == "assistant"]
    else:
        print(f"Run ended with status: {run.status}")
        responses = []

    print(f"Responses: {responses}")  # Debugging line

    return responses
async def generate_image(prompt, quality):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality=quality,
            n=1,
        )
        return response.data[0].url
    except BadRequestError as e:
        if 'content_policy_violation' in str(e):
            return "Your request was rejected due to content policy violation. Please submit a prompt that is safe and follows Discord guidelines."
        else:
            raise e
async def assistant_response3(openai_thread_id=None, prompt=None):
    print(f"OpenAI Thread ID: {openai_thread_id}")  # Debugging line
    # If an OpenAI thread ID is provided, use it, otherwise create a new thread
    if openai_thread_id:
        thread = client.beta.threads.retrieve(openai_thread_id)
    else:
        thread = client.beta.threads.create(messages=[{"role": "user", "content": prompt}])
        openai_thread_id = thread.id  # Store the new OpenAI thread ID
    print(f"Thread: {thread}")  # Debugging line
    # Use the hard-coded assistant ID
    assistant_id = "asst_Zcr8tWsHgMBvbdI9gLcq9p2W" #gpt3 id
    print(f"Assistant ID: {assistant_id}")  # Debugging line
    run = client.beta.threads.runs.create(
        thread_id=openai_thread_id,
        assistant_id=assistant_id,
    )
    # Wait for the run to reach a final state
    while run.status not in ["completed", "expired", "cancelled", "failed"]:
        await asyncio.sleep(1)  # wait for 1 second
        run = client.beta.threads.runs.retrieve(thread_id = run.thread_id, run_id = run.id)  # refresh the run object

    # Check the final status of the run
    if run.status == "completed":
        # Retrieve the assistant's responses
        messages = client.beta.threads.messages.list(thread_id=openai_thread_id)
        responses = [message for message in messages.data if message.role == "assistant"]
    else:
        print(f"Run ended with status: {run.status}")
        responses = []

    print(f"Responses: {responses}")  # Debugging line

    return responses        