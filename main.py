from utilties.Openai_Utils import generate_image, assistant_response
import os
import discord
import openai
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
from openai import OpenAI
from discord import File
from discord.ext import commands
import aiohttp
from utilties.tokenizer import num_tokens_from_string
import chardet
from utilties.youtube_transcript_grabber import get_transcript
from utilties.pplxapi import pplxresponse
import unicodedata
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
        message = await ctx.send(f"{mention} {generated_text}")  # Send the message
        return message  # Return the message object and thread_id
    else:
        # Write the message to a .txt file with line breaks for long lines
        with open('response.txt', 'w') as f:
            words = generated_text.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 140:  # +1 for the space
                    f.write(line + "\n")
                    line = word
                else:
                    line += " " + word if line else word
            if line:  # Write any remaining text
                f.write(line)
        # Send the .txt file as an attachment
        message = await ctx.send(file=File('response.txt'))  # Send and capture the message object
        # Remove the file after sending it
        os.remove('response.txt')
        return message  # Return the message object and thread_id
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
                # Detect the character encoding of the data
                encoding = chardet.detect(data)['encoding']
                # Decode the bytes to a string using the detected encoding
                text = data.decode(encoding)
                # Normalize the text to ensure it's in a consistent form
                # This helps with characters that have multiple possible representations
                text = unicodedata.normalize('NFKC', text)
                # Encode the string to bytes using UTF-8 and then decode to ensure it's JSON serializable
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
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
            prompt = f"{file_prompt}\n{prompt}" if prompt else file_prompt
        else:
            await ctx.send(f"{ctx.author.mention} Please attach a .txt or .py file.")
            return
    return prompt
@bot.command(name='gpt3', help='cheap model 16k token input limit')
async def gpt3(ctx, *, prompt: str = None):
    # Add an eye emoji reaction to the user's command message
    await ctx.message.add_reaction("👀")
    # Handle the prompt (including attached files if any)
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    # Call the assistant and get the response
    responses, thread_id = await assistant_response(prompt=prompt, assistant=3)  # Unpack the tuple correctly
    if not responses:
        await ctx.send(f"{ctx.author.mention} There was an error processing your request.")
        return
    # Get the first assistant message from the structured response
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    # Send the generated text as a message or a file and store the response message
    response_message = await send_text_or_file(ctx, generated_text)
    # Store the thread_id with the message_id as the key
    openai_thread_ids[response_message.id] = thread_id
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
    responses, thread_id, = await assistant_response(prompt=prompt, assistant=4)  # Unpack the tuple correctly
    if not responses:
        await ctx.send(f"{ctx.author.mention} There was an error processing your request.")
        return
    # Get the first assistant message from the structured response
    generated_text = get_first_assistant_message_unstructured(responses) if responses else None
    # Send the generated text as a message or a file and store the response message
    response_message = await send_text_or_file(ctx, generated_text)
    # Store the thread_id with the message_id as the key
    openai_thread_ids[response_message.id] = thread_id
    # Add a check mark reaction to the user's command message after the reply is sent
    await ctx.message.add_reaction("✅")
@bot.command(name='pplx', help='internet model')
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
    await ctx.send(f'The message contains {num_tokens} tokens. Rough input cost: ${num_tokens/100000}')

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
    # If the message is a reply, handle continuing the conversation
    if message.reference:
        referenced_message_id = message.reference.message_id
            # Check if the referenced message ID is in openai_thread_ids
        if referenced_message_id in openai_thread_ids:
                # Retrieve the OpenAI thread ID
            openai_thread_id = openai_thread_ids[referenced_message_id]
                # Add the user's reply to the OpenAI thread
            prompt = message.content  # Assuming you want to use the message content as the prompt
            responses, thread_id = await assistant_response(openai_thread_id=openai_thread_id, prompt=prompt)
            if not responses:
                await message.channel.send("There was an error processing your request.")
                return
            generated_text = get_first_assistant_message_unstructured(responses) if responses else None
                # Create a context object from the message
            ctx = await bot.get_context(message)
                # Send the bot's response in the Discord thread
            response_message = await send_text_or_file(ctx, generated_text)
                # Update the openai_thread_ids with the thread_id
            openai_thread_ids[response_message.id] = thread_id
        else:
            print(f"Referenced message ID is NOT in openai_thread_ids.")
    else:
        # The message is not a reply and will be ignored by on_message handler.
        print("The message is not a reply and will be ignored by on_message handler.")

    # This ensures that the bot's command system can also handle messages
    await bot.process_commands(message)
if __name__ == '__main__':
    bot.run(discord_key)