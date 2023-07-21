from utilties.Openai_Utils import generate_response
import io
import discord
import openai
import asyncio
import textwrap
from utilties.vars import OPENAI_API_KEY, DISCORD_TOKEN
from discord.ext import commands
import aiohttp
from utilties.tokenizer import num_tokens_from_string
from workout_utils.protein_tracking import ProteinTracker
# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.presences - True
bot = commands.Bot(command_prefix='!', intents=intents)
USER_ID = 140224314690502656
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    bot.protein_tracker = ProteinTracker(bot, USER_ID)

async def send_text_or_file(ctx, generated_text):
    async with aiohttp.ClientSession() as session:
        if len(generated_text) <= 2000: 
            mention = ctx.author.mention  # Mention the user who sent the command
            await ctx.send(f"{mention} {generated_text}")
        else:
            # Save to Hastebin
            data = generated_text.encode('utf-8') #data must be bytes
            async with session.post("http://136.36.137.50:7777/documents", data=data) as resp:
                try:
                    data = await resp.json()
                except Exception as e:
                    print(f"An exception occurred: {e}")
                    return
                key = data['key']
                paste_url = f"http://136.36.137.50:7777/{key}"
              
                # Send it 
                await ctx.send(f"{ctx.author.mention} Your generated text was too large to display here, so it was pasted at {paste_url}")  
    
async def read_txt_file(file_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                text = await response.text()
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
@bot.command(name='gpt3', help='Selects the appropriate model based on token length. If token length <= 3500, use gpt-3.5-turbo; else, use gpt-3.5-turbo-16k.')
async def gpt3(ctx, *, prompt: str = None):
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    
    token_length = num_tokens_from_string(prompt, "cl100k_base")

    if token_length <= 3500:
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-3.5-turbo-16k"

    generated_text = await generate_response(model_name, prompt)
    
    print(generated_text)
    await send_text_or_file(ctx, generated_text)

@bot.command(name='gpt4', help='10x cost but much better in reasoning tasks, can intake about 8k tokens')
async def gpt4(ctx, *, prompt: str = None):
    prompt = await handle_prompt(ctx, prompt)
    if prompt is None:
        return
    generated_text = await generate_response("gpt-4-0613", prompt)
    print(generated_text)
    await send_text_or_file(ctx, generated_text)
        
@bot.command(name='gptthread')
async def gptthread(ctx):
    thread = await ctx.channel.create_thread(name=f"GPT Chat with {ctx.author.display_name}", type=discord.ChannelType.public_thread)
    await thread.send(f"{ctx.author.mention} You have started a chat with GPT. Type your messages in this thread using the gpt3t/gpt4t command to consider up to 3k tokens of context\n you may still use gpt4 & gpt3 to get single shot of a specific prompt")

@bot.command(name='privatethread', help='creates a private thread, likely this can be seen by admins')
async def privatethread(ctx):
    thread = await ctx.channel.create_thread(name=f"Private GPT Chat with {ctx.author.display_name}", type=discord.ChannelType.private_thread)
    await thread.send(f"{ctx.author.mention} You have started a private chat with GPT. Type your messages in this thread using the gpt3t/gpt4t command to consider up to 3k tokens of context\n you may still use gpt4 & gpt3 to get single shot of a specific prompt")

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
    num_tokens = num_tokens_from_string(message, "cl100k_base")
    await ctx.send(f'The message contains {num_tokens} tokens.')

@bot.command(name='getuserdata', help='Gets the protein data for a user. Returns a table & graph.')
async def getuserdata(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
    except Exception as e:
        await ctx.send("User not found.")
        return

    tracker = ProteinTracker(bot, user.id)
    user_data, img_path = tracker.get_user_data(user.id)
    await ctx.send(f"```{user_data}```")
    await ctx.send(file=discord.File(img_path))

    
@bot.command(name='manualprotein', help='manual protein entry for if you miss a day. Example usage: !manualprotein User01 12/31/2023 100 "Description of meals"')
async def manualprotein(ctx, user_id: int = None, date: str = None, protein_info: str = None, description_info: str = None):
    if user_id is None or date is None or protein_info is None or description_info is None:
        missing_args = []
        if user_id is None:
            missing_args.append("user_id")
        if date is None:
            missing_args.append("date")
        if protein_info is None:
            missing_args.append("protein_info")
        if description_info is None:
            missing_args.append("description_info")

        await ctx.send(f"Missing arguments: {', '.join(missing_args)}. Please provide all required arguments.")
        return

    try:
        user = await bot.fetch_user(user_id)
    except Exception as e:
        await ctx.send("User not found.")
        return 

    tracker = ProteinTracker(bot, user.id)
    tracker.manual_record_protein_info(date, protein_info, description_info)
    await ctx.send(f"Protein info for {user.name} has been manually updated for {date}.")


@bot.command(name='listusers', help='Lists all the users the bot has connected to in its servers.')
async def list_users(ctx):
    users = []
    for guild in bot.guilds:
        for member in guild.members:
            if member not in users:
                users.append(member)

    user_list = 'Connected users:\n'
    for user in users:
        user_list += f'{user.name}#{user.discriminator}\n'

    await ctx.send(user_list)
    
if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)