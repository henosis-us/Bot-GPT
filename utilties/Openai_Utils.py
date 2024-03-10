# openai_utils.py
import json
from utilties.urlfetch import urlFetch
from openai import OpenAI, BadRequestError
from utilties.pplxapi import pplxresponse
import asyncio
from utilties.anth import anthropicResponse
client = OpenAI()
from utilties.youtube_transcript_grabber import get_transcript
async def fetch_and_prepare_content_for_lm_tool(url):
    try:
        # Since the original function is synchronous, use asyncio to run it in an executor
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, urlFetch, url)
        return content
    except Exception as e:
        print(f"An error occurred while fetching content: {e}")
        return None
async def assistant_response(openai_thread_id=None, prompt=None, assistant=4):
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
    if assistant == 4:
        assistant_id = "asst_z9ChMmBNvr3FucVrXZFZ6vpl"
    else:
        assistant_id = "asst_9JMEFzEZgbbsJEYr4ME6WTsY"

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
                print(f"Raw arguments received: {tool_call.function.arguments}")
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
                if function_name == "get_video_context_response":
                    print("calling video transcript search")
                    output = await get_transcript(arguments["youtube_url"])
                    user_query = arguments["user_query"]  # Extract the user query from the arguments
                    # Prepend "transcript:" to the output and append the user query with a newline
                    # If the transcript is too long, call gpt-4 to summarize it with context from the original prompt
                    print(user_query)
                    if len(output) > 32000:
                        # Prepend "transcript:" to the output and append the user query with a newline
                        output = f"<transcript>{output}</transcript><user_query>{user_query}</user_query>"
                        messages = [{"role": "user", "content": output}]
                        output = await anthropicResponse("claude-3-sonnet-20240229", messages)
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

    return (responses, openai_thread_id)
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
