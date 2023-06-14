import asyncio
import sqlite3
import discord
from discord.ext import tasks
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class ProteinTracker:
    def __init__(self, bot, user_id):
        self.bot = bot
        self.user_id = user_id
        self.awaiting_description = False
        self.user_responded = False
        self.latest_protein_info = None
        # Database setup
        self.conn = sqlite3.connect('protein_data.db')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS user_protein(
                userID TEXT,
                dateTime TEXT,
                protein_info TEXT,
                description_info TEXT
            )
        ''')
        self.conn.commit()

        # Start protein tracker loop when the bot is ready
        self.protein_tracker.start()

    @tasks.loop(hours=24)
    async def protein_tracker(self):
        user = self.bot.get_user(self.user_id)
        if user is not None:
            if not self.user_responded:
                await self.add_placeholder_data()
            await user.send("How many grams of protein did you consume today?")
            self.user_responded = False
        else:
            print(f"Couldn't find user with ID {self.user_id}.")

    async def add_placeholder_data(self):
        now = datetime.now()
        dateTime = now.strftime("%m/%d/%Y, %H:%M:%S")
        with self.conn:
            self.c.execute("INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                      {'userID': self.user_id, 'dateTime': dateTime, 'protein_info': "No response", 'description_info': "No response"})
        print(f"Added placeholder data at {dateTime}.")

    # Start the loop at 11pm
    @protein_tracker.before_loop
    async def before_protein_tracker(self):
        now = datetime.now()
        if now.hour < 23:
            next_run = now.replace(hour=23, minute=0, second=0, microsecond=0)
        else:
            # If it's past 11pm, schedule for 11pm the next day
            next_run = now.replace(day=now.day + 1, hour=23, minute=0, second=0, microsecond=0)
        delta = next_run - now
        print(f"Next protein tracker scheduled for {next_run}. Waiting for {delta.seconds} seconds.")
        await asyncio.sleep(delta.seconds)

    async def record_protein_info(self, message):
        # Only record messages from the specified user in response to the bot
        if message.author.id == self.user_id and message.channel.type == discord.ChannelType.private:
            # Get current date and time
            now = datetime.now()
            dateTime = now.strftime("%m/%d/%Y, %H:%M:%S")
            
            if not self.awaiting_description:
                self.latest_protein_info = message.content
                self.awaiting_description = True
                await message.channel.send("Please provide a quick description of your meals for the day.")
            else:
                # Save data to the database
                with self.conn:
                    self.c.execute("INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                              {'userID': message.author.id, 'dateTime': dateTime, 'protein_info': self.latest_protein_info, 'description_info': message.content})
                print(f"Protein info recorded at {dateTime}.")
                self.awaiting_description = False
                self.user_responded = True

    def get_user_data(self, userID):
        self.c.execute("SELECT * FROM user_protein WHERE userID=:userID", {'userID': userID})
        data = self.c.fetchall()

        # Create a formatted string for the table
        table = "UserID       | DateTime         | Protein Info | Description Info\n"
        table += "-"*72 + "\n"  # Separator line
        for row in data:
            table += f"{row[0]:<13}| {row[1]:<17}| {row[2]:<13}| {row[3]}\n"

        # List for dates and protein info
        dates = []
        protein_info = []

        for row in data:
            dates.append(datetime.strptime(row[1], "%m/%d/%Y, %H:%M:%S"))
            protein_info.append(int(row[2]))  # assuming protein info is an integer

        # Plotting the data
        plt.plot_date(dates, protein_info, linestyle='solid')

        # Format date
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # Rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        plt.gcf().autofmt_xdate()

        plt.title('Protein Intake Over Time')
        plt.xlabel('Date')
        plt.ylabel('Protein (in grams)')

        # Save the graph as an image file
        img_path = f"{userID}_protein_intake.png"
        plt.savefig(img_path)

        # Clear the figure for future plots
        plt.clf()

        return table, img_path

    def manual_record_protein_info(self, dateTime, protein_info, description_info):
        # Get current date and time
        dateTime = datetime.strptime(dateTime, "%m/%d/%Y").strftime("%m/%d/%Y, %H:%M:%S")

        # Save data to the database
        with self.conn:
            self.c.execute("INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                      {'userID': self.user_id, 'dateTime': dateTime, 'protein_info': protein_info, 'description_info': description_info})
        print(f"Protein info recorded at {dateTime}.")
