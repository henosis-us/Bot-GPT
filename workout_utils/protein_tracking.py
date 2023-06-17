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
        self.conn = sqlite3.connect("protein_data.db")
        self.c = self.conn.cursor()
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS user_protein(
                userID TEXT,
                dateTime TEXT,
                protein_info TEXT,
                description_info TEXT
            )
        """
        )
        self.conn.commit()

        # Start protein tracker loop when the bot is ready
        self.protein_tracker.start()

    @tasks.loop(hours=24)
    async def protein_tracker(self):
        user = self.bot.fetch_user(self.user_id)
        if user is not None:
            if not self.user_responded:
                await self.add_placeholder_data()
            await user.send(
                "Please enter the amount of protein (in grams) you consumed today, followed by a quick description of your meals. (Example: 120 protein, chicken and rice)"
            )
            self.user_responded = False
        else:
            print(f"Couldn't find user with ID {self.user_id}.")


    async def add_placeholder_data(self):
        now = datetime.now()
        dateTime = now.strftime("%m/%d/%Y, %H:%M:%S")
        with self.conn:
            self.c.execute(
                "INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                {
                    "userID": self.user_id,
                    "dateTime": dateTime,
                    "protein_info": "No response",
                    "description_info": "No response",
                },
            )
        print(f"Added placeholder data at {dateTime}.")

    # Start the loop at 11pm
    @protein_tracker.before_loop
    async def before_protein_tracker(self):
        now = datetime.now()
        if now.hour < 23:
            next_run = now.replace(hour=23, minute=0, second=0, microsecond=0)
        else:
            # If it's past 11pm, schedule for 11pm the next day
            next_run = now.replace(
                day=now.day + 1, hour=23, minute=0, second=0, microsecond=0
            )
        delta = next_run - now
        print(
            f"Next protein tracker scheduled for {next_run}. Waiting for {delta.seconds} seconds."
        )
        await asyncio.sleep(delta.seconds)

    def manual_record_protein_info(self, dateTime, protein_info, description_info):
        # Check data types
        if not isinstance(dateTime, str):
           print(f"Error: dateTime should be a string, not {type(dateTime).__name__}")
           return
        if not isinstance(protein_info, str):
            print(f"Error: protein_info should be a string, not {type(protein_info).__name__}")
            return
        if not isinstance(description_info, str):
            print(f"Error: description_info should be a string, not {type(description_info).__name__}")
            return

        # Check if protein_info can be converted to an integer
        try:
            protein_info_int = int(protein_info)
        except ValueError:
            print(f"Error: protein_info should be convertible to an integer, but '{protein_info}' could not be converted.")
            return

        # Check if dateTime can be converted to a datetime object
        try:
            datetime.strptime(dateTime, "%m/%d/%Y")
        except ValueError:
            print(f"Error: dateTime should be in the format '%m/%d/%Y', but '{dateTime}' could not be converted.")
            return

    # Get current date and time
        dateTime = datetime.strptime(dateTime, "%m/%d/%Y").strftime("%m/%d/%Y, %H:%M:%S")

    # Save data to the database
        with self.conn:
            self.c.execute(
                "INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                {
                    "userID": self.user_id,
                    "dateTime": dateTime,
                    "protein_info": protein_info_int,
                    "description_info": description_info,
                },
            )
        print(f"Protein info recorded at {dateTime}.")


    def get_user_data(self, userID):
        self.c.execute(
            "SELECT * FROM user_protein WHERE userID=:userID", {"userID": userID}
        )
        data = self.c.fetchall()

        # Create a formatted string for the table
        table = "UserID       | DateTime         | Protein Info | Description Info\n"
        table += "-" * 72 + "\n"  # Separator line
        for row in data:
            table += f"{row[0]:<13}| {row[1]:<17}| {row[2]:<13}| {row[3]}\n"

        # List for dates and protein info
        dates = []
        protein_info = []

        for row in data:
            dates.append(datetime.strptime(row[1], "%m/%d/%Y, %H:%M:%S"))
            protein_info.append(int(row[2]))  # assuming protein info is an integer

        # Plotting the data
        plt.plot_date(dates, protein_info, linestyle="solid")

        # Format date
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # Rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        plt.gcf().autofmt_xdate()

        plt.title("Protein Intake Over Time")
        plt.xlabel("Date")
        plt.ylabel("Protein (in grams)")

        # Save the graph as an image file
        img_path = f"{userID}_protein_intake.png"
        plt.savefig(img_path)

        # Clear the figure for future plots
        plt.clf()

        return table, img_path

    def manual_record_protein_info(self, dateTime, protein_info, description_info):
        # Get current date and time
        dateTime = datetime.strptime(dateTime, "%m/%d/%Y").strftime(
            "%m/%d/%Y, %H:%M:%S"
        )

        # Save data to the database
        with self.conn:
            self.c.execute(
                "INSERT INTO user_protein VALUES (:userID, :dateTime, :protein_info, :description_info)",
                {
                    "userID": self.user_id,
                    "dateTime": dateTime,
                    "protein_info": protein_info,
                    "description_info": description_info,
                },
            )
        print(f"Protein info recorded at {dateTime}.")
