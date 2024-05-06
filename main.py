import asyncio
import time
import json
import os
import discord
import random
import pymongo
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final
from Functions import calculate_wpm
from Functions import calculate_correctness
from Functions import underline_errors
from Functions import update_user_progress

#MongoDb
myclient = pymongo.MongoClient("mongodb+srv://wimmerjakob9:zjt6LQCz7b9qyVEl@typeracebot.nauuy66.mongodb.net/?retryWrites=true&w=majority&appName=TypeRaceBot")
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
async def help(ctx):
    await ctx.response.send_message("Hallo! Ich bin der TypeRaceBot. Hier sind meine Befehle:\n")


@bot.tree.command(name="multiplayer")
async def multiplayer(ctx, num_players: int):
    if num_players < 2:
        await ctx.response.send_message("You need at least 2 players for a multiplayer game.")
        return

    await ctx.response.send_message(f"Multiplayer TypeRace is starting in 3 seconds for {num_players} players!")
    await asyncio.sleep(1)
    message = await ctx.followup.send("Get ready!")
    await asyncio.sleep(1)
    for i in range(3, 0, -1):
        await message.edit(content=str(i))
        await asyncio.sleep(1)
    await message.edit(content="Go!")
    await asyncio.sleep(1)
    await message.edit(content="Type the following sentence as fast as you can!")
    words = random.sample(open("FilesNeeded/randomquotes.csv").readlines(), 15)
    sentence = ' '.join(word.strip() for word in words)
    sentence_message = await ctx.followup.send(sentence)

    start_time = time.time()

    def check(m):
        return m.author != bot.user and m.channel == ctx.channel

    results = []
    for _ in range(num_players):
        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.followup.send("Time is up!")
        else:
            end_time = time.time()
            wpm = calculate_wpm(start_time, end_time, len(words))
            correctness = calculate_correctness(msg.content, sentence)
            underlined_sentence = underline_errors(msg.content, sentence)

            if correctness < 30:
                await ctx.followup.send(f"{msg.author.name}, your test is invalid due to low accuracy.")
            else:
                await ctx.followup.send(
                    f"{msg.author.name}, your words per minute: {wpm}. Correctness: {correctness}%\nYour sentence:\n{underlined_sentence}")
                results.append((msg.author.name, wpm, correctness))

    # Sort the results by wpm and correctness
    results.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Send the winner
    winner = results[0]
    await ctx.followup.send(f"The winner is {winner[0]} with {winner[1]} words per minute and {winner[2]}% correctness!")


@bot.tree.command(name="userrecords")
async def userrecords(ctx, username: str = None):
    if username is None:
        username = ctx.user.name

    user_record = userdata.find_one({"_id": username})

    if user_record is None or 'record' not in user_record:
        await ctx.response.send_message(f"{username} hasn't raced yet.")
    else:
        record_wpm = user_record['record']['wpm']
        accuracy = user_record['record']['accuracy']
        await ctx.response.send_message(f"{username}'s record:\nWords per minute: {record_wpm}\nAccuracy: {accuracy}%")


@bot.tree.command(name="userprogress")
async def userprogress(ctx, username: str = None):
    if username is None:
        username = ctx.user.name

    user_record = userdata.find_one({"_id": username})

    if user_record is None or 'progress' not in user_record:
        await ctx.response.send_message(f"{username} hasn't raced yet.")
    else:
        progress_message = f"{username}'s progress:\n"
        for record in user_record['progress']:
            progress_message += f"Date: {record['date']}, Words per minute: {record['wpm']}, Accuracy: {record['accuracy']}%\n"
        await ctx.response.send_message(progress_message)


@bot.tree.command(name="leaderboard")
async def leaderboard(ctx):
    user_records = userdata.find({})

    sorted_records = sorted(user_records, key=lambda x: x['record']['wpm'], reverse=True)

    top_10_records = sorted_records[:10]

    leaderboard_message = "Leaderboard:\n"
    for i, record in enumerate(top_10_records, start=1):
        username = record['_id']
        stats = record['record']
        leaderboard_message += f"{i}. {username} - WPM: {stats['wpm']}, Accuracy: {stats['accuracy']}%\n"

    await ctx.response.send_message(leaderboard_message)


@bot.tree.command(name="typerace_german")
async def typerace_german(ctx, num_words: int = 15):
    if num_words < 1:
        await ctx.response.send_message("You must type at least 1 word.")
        return

    await ctx.response.send_message("TypeRace is starting in 3 seconds!")
    await asyncio.sleep(1)
    message = await ctx.followup.send("Get ready!")
    await asyncio.sleep(1)
    for i in range(3, 0, -1):
        await message.edit(content=str(i))
        await asyncio.sleep(1)
    await message.edit(content="Go!")
    await asyncio.sleep(1)
    await message.edit(content="Type the following sentence as fast as you can!")
    words = random.sample(open("FilesNeeded/randomquotes.csv").readlines(), num_words)
    sentence = ' '.join(word.strip() for word in words)
    sentence_message = await ctx.followup.send(sentence)

    start_time = time.time()

    def check(m):
        return m.author == ctx.user and m.channel == ctx.channel

    timeout = 900 if num_words != 15 else 60

    try:
        msg = await bot.wait_for('message', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await ctx.followup.send("Time is up!")
    else:
        end_time = time.time()
        wpm = calculate_wpm(start_time, end_time, len(words))
        correctness = calculate_correctness(msg.content, sentence)
        underlined_sentence = underline_errors(msg.content, sentence)

        if correctness < 30:
            await ctx.followup.send("Your test is invalid due to low accuracy.")
        else:
            await ctx.followup.send(
                f"Your words per minute: {wpm}. Correctness: {correctness}%\nYour sentence:\n{underlined_sentence}")

            if num_words == 15:
                uid = ctx.user.id
                user_record = userdata.find_one({"_id": uid})
                update_user_progress(userdata, uid, wpm, correctness)

                if user_record is None or wpm > user_record['record']['wpm']:
                    userdata.update_one({"_id": uid}, {"$set": {"record": {"wpm": wpm, "accuracy": correctness}}})


bot.run(TOKEN)
