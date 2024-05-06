import asyncio
import time
import json
import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final
from Functions import calculate_wpm
from Functions import calculate_correctness
from Functions import underline_errors
from Functions import update_user_progress

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
    await ctx.response.send_message("Commands: /typerace - Start a TypeRace game")


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
    with open('UserData/userrecords.json', 'r') as f:
        user_records = json.load(f)

    if username is None:
        username = ctx.user.name

    user_record = user_records.get(username)

    if user_record is None:
        await ctx.response.send_message(f"{username} hasn't raced yet.")
    else:
        record_wpm = user_record['record_wpm']
        accuracy = user_record['accuracy']
        await ctx.response.send_message(f"{username}'s record:\nWords per minute: {record_wpm}\nAccuracy: {accuracy}%")


@bot.tree.command(name="userprogress")
async def userprogress(ctx, username: str = None):
    with open('UserData/userprogress.json', 'r') as f:
        user_progress = json.load(f)

    if username is None:
        username = ctx.user.name

    user_records = user_progress.get(username)

    if user_records is None:
        await ctx.response.send_message(f"{username} hasn't raced yet.")
    else:
        progress_message = f"{username}'s progress:\n"
        for record in user_records:
            progress_message += f"Date: {record['date']}, Words per minute: {record['wpm']}, Accuracy: {record['accuracy']}%\n"
        await ctx.response.send_message(progress_message)


@bot.tree.command(name="leaderboard")
async def leaderboard(ctx):
    with open('UserData/userrecords.json', 'r') as f:
        user_records = json.load(f)

    sorted_records = sorted(user_records.items(), key=lambda x: x[1]['record_wpm'], reverse=True)

    top_10_records = sorted_records[:10]

    leaderboard_message = "Leaderboard:\n"
    for i, record in enumerate(top_10_records, start=1):
        username, stats = record
        leaderboard_message += f"{i}. {username} - WPM: {stats['record_wpm']}, Accuracy: {stats['accuracy']}%\n"

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
                with open('UserData/userrecords.json', 'r') as f:
                    user_records = json.load(f)

                username = ctx.user.name
                user_record = user_records.get(username, {'record_wpm': 0, 'accuracy': 0})
                update_user_progress(username, wpm, correctness)

                if wpm > user_record['record_wpm']:
                    user_record['record_wpm'] = wpm
                    user_record['accuracy'] = correctness
                    user_records[username] = user_record

                    with open('UserData/userrecords.json', 'w') as f:
                        json.dump(user_records, f)


bot.run(TOKEN)
