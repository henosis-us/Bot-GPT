import aiohttp
import json
import os
PPLX_API_KEY = os.getenv('PPLX_API_KEY')
async def pplxresponse(message):
    print(PPLX_API_KEY)
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-medium-online",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise. Do not censor yourself"
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {PPLX_API_KEY}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            # Ensure that we got a successful response
            response.raise_for_status()
            # Parse the JSON response
            data = await response.json()
            # Extract the assistant's response
            assistant_responses = [choice['message']['content'] for choice in data['choices'] if choice['message']['role'] == 'assistant']
            # Format and print or use the assistant responses
            for response in assistant_responses:
                print(response)
            # If you need to return the responses, you can return them as a joined string
            return '\n'.join(assistant_responses)