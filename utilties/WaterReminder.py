from discord.ext import tasks, commands
import discord
from datetime import datetime, timedelta
from sqlite3 import connect
import matplotlib.pyplot as plt

# Define the water reminder task
@tasks.loop(hours=1)
async def water_reminder(bot, USER_IDS):
    now = datetime.now()
    if 9 <= now.hour < 22:  # Between 9am and 10pm
        for USER_ID in USER_IDS:
            user = await bot.fetch_user(USER_ID)
            if user is not None:
                ounces_drunk = (now.hour - 9) * 9.85  # 9.85 ounces per hour
                gallons_drunk = ounces_drunk / 128  # 128 ounces in a gallon
                await user.send(f"Hey there! Just a friendly reminder to drink your water. You should have consumed approximately {gallons_drunk:.2f} gallons by now. Keep going!")
            else:
                print(f"User with ID {USER_ID} not found.")
    else:
        print("Outside of reminder hours.")
