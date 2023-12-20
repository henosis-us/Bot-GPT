import aiohttp
import json

async def pplxresponse(message):
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "pplx-70b-online",
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
        "authorization": "Bearer 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"
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