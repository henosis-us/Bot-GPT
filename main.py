from utilties.Openai_Utils import generate_image, assistant_response, assistant_response3
import os
import discord
import openai
from vars import OPENAI_API_KEY, DISCORD_TOKEN
from openai import OpenAI
from discord import File
from discord.ext import commands
import aiohttp
from utilties.tokenizer import num_tokens_from_string
import chardet
from youtube_transcript_grabber import get_transcript
from pplxapi import pplxresponse
openai_api_key = OPENAI_API_KEY
# Set up OpenAI API
client = OpenAI(api_key=openai_api_key)
discord_key = DISCORD_TOKEN
# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.presences - True
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
async def send_text_or_file(ctx, generated_text):
    if len(generated_text) <= 1500: 
        mention = ctx.author.mention  # Mention the user who sent the command
        return await ctx.send(f"{mention} {generated_text}")  # Return the message object
    else:
        # Write the message to a .txt file
        with open('response.txt', 'w') as f:
            f.write(generated_text)
        # Send the .txt file as an attachment
        message = await ctx.send(file=File('response.txt'))  # Send and capture the message object
        # Remove the file after sending it
        os.remove('response.txt')
        return message  # Return the message object
def get_first_assistant_message_unstructured(data):
    # Loop through the messages to find the first one with the role 'assistant'
    for message in data:
        # Check if the role is 'assistant'
        if message.role == "assistant":
            # Return the text value of the first 'text' content
            for content in message.content:
                if content.type == "text":
                    return content.text.value
    return None    
        
async def read_txt_file(file_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                data = await response.read()
                encoding = chardet.detect(data)['encoding']
                text = data.decode(encoding).encode('utf-8')
                return text
            else:
                return None
async def handle_prompt(ctx, prompt):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.txt') or attachment.filename.endswith('.py'):
            file_url = attachment.url
            file_prompt = await read_txt_file(file_url)
            if file_prompt is None:
                await ctx.send(f"{ctx.author.mention} Failed to read the attached file.")
                return
            prompt = f"{prompt}\n{file_prompt}" if prompt else file_prompt
        else:
            await ctx.send(f"{ctx.author.mention} Please attach a .txt or .py file.")
            return
    return prompt
##commands
@bot.command(name='gpt3', help='Selects the appropriate model based on token length. If token length <= 16000, use gpt-3.5-turbo-1106; else, use gpt-4-1106-preview.')
async def gpt3(ctx, *, prompt: str = None):
    # Add an eye emoji reaction to the user's command message
    await ctx.message.add_reaction("👀")
    # Handle the prompt (including attached files if any)
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    # Call the assistant and get the response
    responses = await assistant_response3(prompt=prompt)
    if not responses:
        await ctx.send(f"{ctx.author.mention} There was an error processing your request.")
        return
    # Extract the thread_id from the response
    thread_id = responses[0].thread_id
    response_message = await send_text_or_file(ctx, generated_text)
    # Store the thread_id with the message_id as the key
    openai_thread_ids[response_message.id] = thread_id
    # Get the first assistant message from the structured response
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    # Send the generated text as a message or a file
    await send_text_or_file(ctx, generated_text)
    # Add a check mark reaction to the user's command message after the reply is sent
    await ctx.message.add_reaction("✅")
@bot.command(name='gpt4', help='10x cost but much better in reasoning tasks, can intake about 128k tokens')
async def gpt4(ctx, *, prompt: str = None):
    # Add an eye emoji reaction to the user's command message
    await ctx.message.add_reaction("👀")
    # Handle the prompt (including attached files if any)
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    # Call the assistant and get the response
    responses = await assistant_response(prompt=prompt)
    if not responses:
        await ctx.send(f"{ctx.author.mention} There was an error processing your request.")
        return
    # Extract the thread_id from the response
    thread_id = responses[0].thread_id
    # Get the first assistant message from the structured response
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    # Send the generated text as a message or a file and store the response message
    response_message = await send_text_or_file(ctx, generated_text)
    # Store the thread_id with the response message_id as the key
    openai_thread_ids[response_message.id] = thread_id
    # Add a check mark reaction to the user's command message after the reply is sent
    await ctx.message.add_reaction("✅")
@bot.command(name='hermes')
async def hermes(ctx, *, user_message: str = None):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.txt'):
            file_url = attachment.url
            user_message = await read_txt_file(file_url)
            if user_message is None:
                await ctx.send(f"{ctx.author.mention} Failed to read the attached file.")
                return
        else:
            await ctx.send(f"{ctx.author.mention} Please attach a .txt file.")
            return
    if user_message is None:
        await ctx.send(f"{ctx.author.mention} Please provide a message.")
        return
    response = await pplxresponse(user_message)
    await send_text_or_file(ctx, response)
@bot.command(name='transcript')
async def transcript(ctx, *, url: str):
    transcript_text = await get_transcript(url)
    await send_text_or_file(ctx, transcript_text)
@bot.command(name='gpt')
async def gpt(ctx, *, prompt: str):
    if ' ' in prompt:
        mention = ctx.author.mention  # Mention the user who sent the command
        await ctx.send(f"{mention} You accidentally used a space :D")
    else:
        mention = ctx.author.mention  # Mention the user who sent the command
        await ctx.send(f"{mention} Your prompt doesn't contain a space.")
@bot.command(name='tokens', help='rough token count using gpt4 chat spec')
async def tokens(ctx, *, message: str = None):
    if ctx.message.attachments:
        
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith('.txt'):
            file_url = attachment.url
            file_text = await read_txt_file(file_url)
            if file_text is None:
                await ctx.send(f"{ctx.author.mention} Failed to read the attached file.")
                return
            
            message = file_text
        else:
            await ctx.send(f"{ctx.author.mention} Please attach a .txt file.")
            return
    num_tokens = num_tokens_from_string(message)
    await ctx.send(f'The message contains {num_tokens} tokens.')

@bot.command(name='dalle3', help='Generates an image using DALL-E 3 model. --q for higher quality at double cost')
async def dalle3(ctx, *, prompt: str = None):
    if prompt is None:
        await ctx.send(f"{ctx.author.mention} Please provide a prompt.")
        return

    # Check if the prompt contains the quality flag
    quality = "standard"
    if "--q" in prompt:
        quality = "hd"
        prompt = prompt.replace("--q", "").strip()  # Remove the flag from the prompt

    image_url = await generate_image(prompt, quality)
    await ctx.send(image_url)
created_threads = set()
openai_thread_ids = {}
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Debug: Print the current state of openai_thread_ids
    print(f"Current openai_thread_ids: {openai_thread_ids}")

    # Debug: Print message reference
    print(f"Message reference: {message.reference}")

    # If the message is a reply, handle continuing the conversation
    if message.reference:
        referenced_message_id = message.reference.message_id
        # Check if the referenced message ID is in openai_thread_ids
        if referenced_message_id in openai_thread_ids:
            # Retrieve the OpenAI thread ID
            openai_thread_id = openai_thread_ids[referenced_message_id]
            # Add the user's reply to the OpenAI thread
            prompt = message.content  # Assuming you want to use the message content as the prompt
            responses = await assistant_response(openai_thread_id=openai_thread_id, prompt=prompt)
            generated_text = get_first_assistant_message_unstructured(responses) if responses else None
            # Create a context object from the message
            ctx = await bot.get_context(message)
            # Send the bot's response in the Discord thread
            await send_text_or_file(ctx, generated_text)
        else:
            print(f"Referenced message ID is NOT in openai_thread_ids.")
    else:
        # The message is not a reply and will be ignored by on_message handler.
        print("The message is not a reply and will be ignored by on_message handler.")

    # This ensures that the bot's command system can also handle messages
    await bot.process_commands(message)
if __name__ == '__main__':
    bot.run(discord_key)