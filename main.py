import asyncio
import time
import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final
from Functions import calculate_wpm
from Functions import calculate_correctness

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


@bot.tree.command(name="typerace")
async def typerace(ctx):
    await ctx.response.send_message("TypeRace is starting in 3 seconds!")
    await asyncio.sleep(1)
    await ctx.followup.send("Get ready!")
    await asyncio.sleep(1)
    for i in range(3, 0, -1):
        await ctx.followup.send(str(i))
        await asyncio.sleep(1)
    await ctx.followup.send("Go!")
    await asyncio.sleep(1)
    await ctx.followup.send("Type the following sentence as fast as you can!")
    words = random.sample(open("NeededFiles/randomquotes.csv").readlines(), 20)
    sentence = ' '.join(word.strip() for word in words)
    await ctx.followup.send(sentence)

    start_time = time.time()

    def check(m):
        return m.author == ctx.user and m.channel.id == ctx.channel_id

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await ctx.followup.send("Time is up!")
    else:
        end_time = time.time()
        wpm = calculate_wpm(start_time, end_time, len(words))
        correctness = calculate_correctness(msg.content, sentence)
        await ctx.followup.send(f"Your words per minute: {wpm}. Correctness: {correctness}%")


bot.run(TOKEN)
