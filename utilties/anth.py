import anthropic
import os
async def anthropicResponse(model, messages):
    # Initialize the Anthropic client with your API key
    client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    try:
        # Use the client to create a message
        message = client.messages.create(
            model=model,
            max_tokens=3096,
            temperature=0.2,
            messages=messages
        )
        print(message)
        # Extract just the assistant's response from the message output
        assistant_response = message.content[0].text
        # Update the message variable with the assistant's response
        message = assistant_response
        return message
    except anthropic.InternalServerError as e:
        if e.status_code == 529:
            print("The Anthropic API is currently overloaded. Please try again later.")
            return "The Anthropic API is currently overloaded. Please try again later."
        else:
            raise
    except Exception as e:
        print(f"An error occurred while processing the request: {e}")
        return f"An error occurred while processing the request: {e}"
"""
from anthropic_tools.tool_use_package.tools.base_tool import BaseTool
from anthropic_tools.tool_use_package.tool_user import ToolUser
from .Openai_Utils import generate_image
from .urlfetch import urlFetch
from .youtube_transcript_grabber import get_transcript
from .pplxapi import pplxresponse

class GenerateImageTool(BaseTool):
    "Tool to generate an image using DALL-E 3."
    def use_tool(self, prompt, quality):
        return generate_image(prompt, quality)

class GetTranscriptTool(BaseTool):
    "Tool to retrieve relevant answer from a YouTube video."
    def use_tool(self, youtube_url):
        return get_transcript(youtube_url)

class QueryLLMInternetTool(BaseTool):
    "Tool to query a language model with internet access."
    async def use_tool(self, query):
        try:
            output = await pplxresponse(query)
            if output:
                return output
            else:
                print("ALERT NO LLM OUTPUT: pplxresponse returned None or empty string.")
                return "Error: No output received from the language model."
        except Exception as e:
            print(f"An error occurred while awaiting pplxresponse: {e}")
            return f"Error: An exception occurred - {e}"

class URLFetchTool(BaseTool):
    "Tool to fetch the content of a webpage as plain text."
    def use_tool(self, url):
        return urlFetch(url)

generate_image_tool = GenerateImageTool(
    name="generate_image",
    description="Generate an image using DALL-E 3",
    parameters=[
        {"name": "prompt", "type": "string", "description": "The prompt for DALL-E 3"},
        {"name": "quality", "type": "string", "description": "The quality of the image, either 'standard' or 'hd'"}
    ]
)

get_video_transcript = GetTranscriptTool(
    name="get_transcript",
    description="get the transcript of a youtube video link if the user asks something about it's context",
    parameters=[
        {"name": "youtube_url", "type": "string", "description": "The full URL of the YouTube video"}
    ]
)

query_llm_internet_tool = QueryLLMInternetTool(
    name="query_llm_internet",
    description="Query a language model with internet access to obtain grounded and up-to-date information, 90% accuracy rate please let the user know if any information seems incorrect",
    parameters=[
        {"name": "query", "type": "string", "description": "The input query for the language model to process and provide information on"}
    ]
)

url_fetch_tool = URLFetchTool(
    name="urlFetch",
    description="Fetch the content of a webpage as plain text",
    parameters=[
        {"name": "url", "type": "string", "description": "The URL of the webpage to fetch"}
    ]
)

async def anthropicResponse(model, messages):
    # Initialize the Anthropic client with your API key
    client = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

    tool_user = ToolUser([generate_image_tool, get_video_transcript, query_llm_internet_tool, url_fetch_tool])

    try:
        # Use the tool_user to process the messages and generate a response
        response = await tool_user.use_tools(messages, execution_mode='automatic')
        return response
    except anthropic.InternalServerError as e:
        if e.status_code == 529:
            print("The Anthropic API is currently overloaded. Please try again later.")
            return "The Anthropic API is currently overloaded. Please try again later."
        else:
            raise
    except Exception as e:
        print(f"An error occurred while processing the request: {e}")
        return f"An error occurred while processing the request: {e}"
"""
