# openai_utils.py
import openai
import asyncio

async def generate_response(model_name, prompt):
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant, please markdown all code with highlight.js style"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        generated_text = response['choices'][0]['message']['content'].strip()
        return generated_text

    except openai.error.RateLimitError as e:
        asyncio.sleep(3)  # Wait for a few seconds before retrying
        return await generate_response(model_name, prompt)