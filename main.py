import asyncio
import time
import os
import discord
import random
import pymongo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dotenv import load_dotenv
from discord.ext import commands
from typing import Final
from Functions import calculate_wpm
from Functions import calculate_correctness
from Functions import underline_errors
from Functions import update_user_progress
from datetime import datetime
from Functions import text_to_image

#MongoDb
load_dotenv()
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
myclient = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
mydb = myclient["TypeRaceBot"]
userdata = mydb["User"]

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Bot ist Startklar!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="help")
async def help(interaction):
    embed = discord.Embed(title="🤖 TypeRaceBot Help", description="Hello! I'm the TypeRaceBot. Here are my commands:", color=0xD22B2B)
    embed.add_field(name="🏁 typerace [language] [num_words]", value="Starts a TypeRace game. Available languages: English, German, Spanish", inline=False)
    embed.add_field(name="👥 multiplayer [num_players] [language]", value="Starts a Multiplayer TypeRace game. Available languages: English, German, Spanish", inline=False)
    embed.add_field(name="📊 userrecords [member]", value="Shows the records of a member", inline=False)
    embed.add_field(name="📈 userprogress [member]", value="Shows the progress of a member", inline=False)
    embed.add_field(name="🏆 leaderboard", value="Shows the top 10 records", inline=False)
    embed.add_field(name="🎓 experience [member]", value="Shows the experience and level of a member", inline=False)
    embed.add_field(name="📅 typinghistory [member]", value="Shows the typing history of a member", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="userprogress")
async def userprogress(interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    uuid = member.id

    user_record = userdata.find_one({"_id": uuid})

    if user_record is None or 'progress' not in user_record:
        await interaction.response.send_message(f"<@{uuid}> hasn't raced yet.")
    else:
        dates = [datetime.fromisoformat(record['date']) for record in user_record['progress']]
        wpms = [record['wpm'] for record in user_record['progress']]
        accuracies = [record['accuracy'] for record in user_record['progress']]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))

        plt.style.use('dark_background')
        fig.patch.set_facecolor('#36393F')

        color = 'white'
        ax1.set_facecolor('#36393F')
        ax1.set_xlabel('Date', fontsize=14, fontweight='bold', color=color)
        ax1.set_ylabel('Words per minute', color=color, fontsize=14, fontweight='bold')
        ax1.plot(dates, wpms, marker='o', color=color, linewidth=3)
        ax1.tick_params(axis='y', labelcolor=color, labelsize=12)

        ax2.set_facecolor('#36393F')
        ax2.set_xlabel('Date', fontsize=14, fontweight='bold', color=color)
        ax2.set_ylabel('Accuracy (%)', color=color, fontsize=14, fontweight='bold')
        ax2.plot(dates, accuracies, marker='o', color=color, linewidth=3)
        ax2.tick_params(axis='y', labelcolor=color, labelsize=12)

        fig.tight_layout()
        plt.grid(False)
        plt.savefig('progress.png', facecolor=fig.get_facecolor(), edgecolor='none')

        await interaction.response.send_message(file=discord.File('progress.png'))


@bot.tree.command(name="multiplayer")
async def multiplayer(interaction, num_players: int, language: str = "English"):
    if num_players < 2:
        await interaction.response.send_message("You need at least 2 players for a multiplayer game.")
        return

    await interaction.response.send_message(f"Multiplayer TypeRace in {language} is starting in 3 seconds for {num_players} players!")
    await asyncio.sleep(1)
    message = await interaction.followup.send("Get ready!")
    await asyncio.sleep(1)
    for i in range(3, 0, -1):
        await message.edit(content=str(i))
        await asyncio.sleep(1)
    await message.edit(content="Go!")
    await asyncio.sleep(1)
    await message.edit(content="Type the following sentence as fast as you can!")
    words = random.sample(open(f"FilesNeeded/randomquotes_{language}.csv").readlines(), 15)
    sentence = ' '.join(word.strip() for word in words)
    img_io = text_to_image(sentence)

    await interaction.followup.send(file=discord.File(img_io, filename='image.jpeg'))

    start_time = time.time()

    def check(m):
        return m.author != bot.user and m.channel == interaction.channel

    results = []
    for _ in range(num_players):
        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("Time is up!")
        else:
            end_time = time.time()
            wpm = calculate_wpm(start_time, end_time, len(words))
            correctness = calculate_correctness(msg.content, sentence)
            underlined_sentence = underline_errors(msg.content, sentence)

            if correctness < 30:
                await interaction.followup.send(f"{msg.author.name}, your test is invalid due to low accuracy.")
            else:
                await interaction.followup.send(
                    f"{msg.author.name}, your words per minute: {wpm}. Correctness: {correctness}%\nYour sentence:\n{underlined_sentence}")
                results.append((msg.author.name, wpm, correctness))

    # Sort the results by wpm and correctness
    results.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Send the winner
    winner = results[0]
    await interaction.followup.send(
        f"The winner is {winner[0]} with {winner[1]} words per minute and {winner[2]}% correctness!")


@bot.tree.command(name="userrecords")
async def userrecords(interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    uuid = member.id

    user_record = userdata.find_one({"_id": uuid})

    if user_record is None or 'record' not in user_record:
        await interaction.response.send_message(f"<@{uuid}> hasn't raced yet.")
    else:
        # Fetch and format the user's data
        record_wpm = user_record['record']['wpm']
        accuracy = user_record['record']['accuracy']
        language_used = user_record['record']['language']

        embed = discord.Embed(title=f"📊 {member.name}'s Records", description=f"Here are the records for <@{uuid}>:", color=0x00ff00)
        embed.add_field(name="🚀 Words per minute", value=record_wpm, inline=False)
        embed.add_field(name="🎯 Accuracy", value=f"{accuracy}%", inline=False)
        embed.add_field(name="🌐 Language", value=language_used, inline=False)

        await interaction.response.send_message(embed=embed)


class PaginationView(discord.ui.View):
    def __init__(self, member, user_record):
        super().__init__()
        self.member = member
        self.user_record = user_record
        self.current_page = 0

    async def get_embed(self):
        embed = discord.Embed(title=f"{self.member.name}'s Progress", description=f"Here is the progress for <@{self.member.id}>:", color=0xD22B2B)
        for record in self.user_record['progress'][self.current_page*10:(self.current_page+1)*10]:
            date = datetime.fromisoformat(record['date']).strftime('%Y-%m-%d %H:%M:%S')  # Clean up the date
            embed.add_field(name=f"📅 Date: {date}", value=f"🚀 Words per minute: {record['wpm']}, 🎯 Accuracy: {record['accuracy']}% in {record['language']}", inline=False)
        return embed

    @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        embed = await self.get_embed()
        await interaction.response.edit_message(embed=embed)


@bot.tree.command(name="typinghistory")
async def typinghistory(interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    uuid = member.id

    user_record = userdata.find_one({"_id": uuid})

    if user_record is None or 'progress' not in user_record:
        await interaction.response.send_message(f"<@{uuid}> hasn't raced yet.")
    else:
        view = PaginationView(member, user_record)
        embed = await view.get_embed()
        await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="leaderboard")
async def leaderboard(interaction):
    user_records = userdata.find({})

    sorted_records = sorted(user_records, key=lambda x: x['record']['wpm'], reverse=True)

    top_10_records = sorted_records[:10]

    embed = discord.Embed(title="🏆 Leaderboard", description="Here are the top 10 players:", color=0xD22B2B)
    for i, record in enumerate(top_10_records, start=1):
        uuid = record['_id']
        user = await bot.fetch_user(uuid)  # Fetch the user object from the user ID
        username = user.name  # Get the username from the user object
        stats = record['record']
        embed.add_field(name=f"{i}. {username}", value=f"🚀 WPM: {stats['wpm']}, 🎯 Accuracy: {stats['accuracy']}% in {stats['language']}", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="typerace")
async def typerace(interaction, language: str = None, num_words: int = 15):
    if language is None:
        language = "English"

    if num_words < 1:
        await interaction.response.send_message("You must type at least 1 word.")
        return

    words = random.sample(open(f"FilesNeeded/randomquotes_{language}.csv").readlines(), num_words)

    await interaction.response.send_message("TypeRace is starting in 3 seconds!")
    await asyncio.sleep(1)
    message = await interaction.followup.send("Get ready!")
    await asyncio.sleep(1)
    for i in range(3, 0, -1):
        await message.edit(content=str(i))
        await asyncio.sleep(1)
    await message.edit(content="Go!")
    await asyncio.sleep(1)
    await message.edit(content="Type the following sentence as fast as you can!")
    sentence = ' '.join(word.strip() for word in words)
    img_io = text_to_image(sentence)

    await interaction.followup.send(file=discord.File(img_io, filename='image.jpeg'))

    start_time = time.time()

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    timeout = 900 if num_words != 15 else 60

    try:
        msg = await bot.wait_for('message', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await interaction.followup.send("Time is up!")
    else:
        end_time = time.time()
        wpm = calculate_wpm(start_time, end_time, len(words))
        correctness = calculate_correctness(msg.content, sentence)
        underlined_sentence = underline_errors(msg.content, sentence)

        if correctness < 30:
            await interaction.followup.send("Your test is invalid due to low accuracy.")
        else:
            await interaction.followup.send(
                f"Your words per minute: {wpm}. Correctness: {correctness}%\nYour sentence:\n{underlined_sentence}")

            if num_words == 15:
                uid = interaction.user.id
                user_record = userdata.find_one({"_id": uid})

                # Check if 'xp' and 'level' fields exist in the user's record
                if user_record is not None:
                    if 'xp' not in user_record:
                        user_record['xp'] = 0
                    if 'level' not in user_record:
                        user_record['level'] = 1

                    update_user_progress(userdata, uid, wpm, correctness, language)

                    if user_record is None or wpm > user_record['record']['wpm']:
                        userdata.update_one({"_id": uid}, {
                            "$set": {"record": {"wpm": wpm, "accuracy": correctness, "language": language}}})


@bot.tree.command(name="experience")
async def experience(interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    uuid = member.id

    user_record = userdata.find_one({"_id": uuid})

    if user_record is None:
        await interaction.response.send_message(f"<@{uuid}> hasn't raced yet.")
    else:
        # Check if 'xp' and 'level' fields exist in the user's record
        if 'xp' not in user_record:
            user_record['xp'] = 0
        if 'level' not in user_record:
            user_record['level'] = 1

        xp = user_record['xp']
        level = user_record['level']

        embed = discord.Embed(title=f"{member.name}'s Experience", description=f"Here is the experience for <@{uuid}>:",
                              color=0x00ff00)
        embed.add_field(name="🎓 Level", value=level, inline=False)
        embed.add_field(name="🌟 XP", value=xp, inline=False)

        await interaction.response.send_message(embed=embed)

bot.run(TOKEN)