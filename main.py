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
        await ctx.send(f"{mention} {generated_text}")
    else:
        # Write the message to a .txt file
        with open('response.txt', 'w') as f:
            f.write(generated_text)
        # Send the .txt file as an attachment
        await ctx.send(file=File('response.txt'))
        # Remove the file after sending it
        os.remove('response.txt')
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
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    responses = await assistant_response3(prompt=prompt)
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    await send_text_or_file(ctx, generated_text)
    # Add a check mark reaction to the user's command message after the reply is sent
    await ctx.message.add_reaction("✅")
@bot.command(name='gpt4', help='10x cost but much better in reasoning tasks, can intake about 128k tokens')
async def gpt4(ctx, *, prompt: str = None):
    # Add an eye emoji reaction to the user's command message
    await ctx.message.add_reaction("👀")
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    responses = await assistant_response(prompt=prompt)
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    await send_text_or_file(ctx, generated_text)
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
    # Currently, we do nothing with direct messages (DMs)
    if isinstance(message.channel, discord.DMChannel):
        pass
    else:
# Check if the bot is replied to        
        if message.reference and message.reference.resolved.author == bot.user:
            # Process attachments if any
            replied_message = message.reference.resolved.content
            if message.reference.resolved.attachments:
                attachment = message.reference.resolved.attachments[0]
                if attachment.filename.endswith('.txt'):
                    # Download the file and read its content
                    file_content = await read_txt_file(attachment.url)
                    replied_message = file_content if file_content else replied_message
            # Concatenate the bot's message and the user's reply
            if isinstance(replied_message, bytes):
                replied_message = replied_message.decode('utf-8')
            combined_message = "bot message: " + replied_message + "\nuser message: " + message.content        
            # Initialize thread and openai_thread_id
            thread = None
            openai_thread_id = None
            # Generate a thread name using the GPT-3.5-turbo-1106 model. The prompt is the message content, and we ask the model to summarize it into a thread title
            try:
                print(message.content)
                responses = await assistant_response3(prompt=f"Summarize this into a short title: {combined_message}")
                thread_name = get_first_assistant_message_unstructured(responses) if responses else None
                print(f"Generated thread name: {thread_name}")
                thread_name = thread_name[:100].strip()
                thread = await message.channel.create_thread(name=thread_name)
                print("Thread created successfully")
                await thread.add_user(message.author)
                print("User added to thread successfully")
            except Exception as e:
                print(f"Exception caught: {e}")
                # If the generated thread name is empty or only contains whitespace, we use a default name. The default name is "Thread with" followed by the display name of the author of the message
                if not thread_name or thread_name.isspace():
                    thread_name = f"Thread with {message.author.display_name}"
                # Create a new thread in the Discord channel where the message was sent. The name of the thread is the generated or default name
                thread = await message.channel.create_thread(name=thread_name)
            # Add the ID of the created thread to the set of IDs of threads created by the bot
            created_threads.add(thread.id)
            # Check if the combined message is longer than 2000 characters
            if len(combined_message) > 2000:
                # If it is, split the message into chunks of 2000 characters and send each chunk as a separate message
                for i in range(0, len(combined_message), 2000):
                    await thread.send(combined_message[i:i+2000])
            else:
                # If the combined message is not longer than 2000 characters, send it as is
                await thread.send(combined_message)
            # Create a message in the OpenAI thread for the message being replied to and the user's reply
            message_thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"bot message: {replied_message}"
                    },
                    {
                        "role": "user",
                        "content": f"user message: {message.content}"
                    }                
                ]
            )
            thread_content = openai.beta.threads.messages.list(str(message_thread.id))
            # Store the ID of the OpenAI thread in a dictionary, using the ID of the Discord thread as the key
            openai_thread_ids[thread.id] = message_thread.id
            # Store the ID of the OpenAI thread in a variable for later use
            openai_thread_id = message_thread.id
            # Add a reaction of an eye emoji to the user reply
            await message.add_reaction("👁️")
            # Get the assistant's responses
            responses = await assistant_response(openai_thread_id)
            if not responses:
                print("error no response")
                response = "oopsie"
            # Get the updated thread
            thread_messages = client.beta.threads.messages.list(openai_thread_id)
            last_message = get_first_assistant_message_unstructured(thread_messages.data)
            # Send the last message to the Discord thread
            last_message_content = last_message
            # Check if the message is longer than 2000 characters
            if len(last_message_content) > 2000:
                # If it is, split the message into chunks of 2000 characters and send each chunk as a separate message
                for i in range(0, len(last_message_content), 2000):
                    await thread.send(last_message_content[i:i+2000])
            else:
                # If the message is not longer than 2000 characters, send it as is
                await thread.send(last_message_content)
        if message.channel.id in created_threads:
            # Handle the message in the thread
            openai_thread_id = openai_thread_ids[message.channel.id]
            # Add the user's message to the OpenAI thread
            client.beta.threads.messages.create(
                thread_id=openai_thread_id,
                role="user",
                content=message.content
            )
            # Get the assistant's responses
            responses = await assistant_response(openai_thread_id)
            if not responses:
                print("error no response")
                response = "oopsie"
            # Get the updated thread
            thread_messages = client.beta.threads.messages.list(openai_thread_id)
            last_message = get_first_assistant_message_unstructured(thread_messages.data)
            # Send the last message to the Discord thread
            last_message_content = last_message
            # Check if the message is longer than 2000 characters
            if len(last_message_content) > 2000:
                # If it is, split the message into chunks of 2000 characters and send each chunk as a separate message
                for i in range(0, len(last_message_content), 2000):
                    await message.channel.send(last_message_content[i:i+2000])
            else:
                # If the message is not longer than 2000 characters, send it as is
                await message.channel.send(last_message_content)
            return
        # This ensures that the bot's command system can also handle messages
        await bot.process_commands(message)
if __name__ == '__main__':
    bot.run(discord_key)