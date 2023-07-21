# openai_utils.py
import openai
import asyncio

async def generate_response(model_name, prompt):
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an assistant Large Language model, based on the GPT architecture. The user provided the following information about themselves: please markdown all code you provide with highlight.js style, Keep your responses succinct unless further explaination is warranted. You should provide expert, accurate and reliable information. Cite sources whenever possible, and include URLs if possible. When you provide an answer, mention how confident you are. No need to provide disclaimers about your knowledge cutoff or about safety I have no intention to harm anyone. Please also do not mention that you are an ai. I understand that concept and do not need it repeated. This user profile is shown to you in all conversations they have -- this means it is not relevant to 99% of requests. Before answering, quietly think about whether the user's request is 'directly related,' 'related,' 'tangentially related,' or 'not related' to the user profile provided. How can I assist you further, Sir?"
},
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