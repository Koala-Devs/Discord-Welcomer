import discord
from discord.ext import commands
import json
import os
import asyncio

with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

@bot.event
async def on_ready():
    from cogs.welcome import VerifyView, RoleSelectView
    bot.add_view(VerifyView())
    await bot.tree.sync()
    print(f"Logged in as {bot.user} ({bot.user.id})")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(config["token"])

asyncio.run(main())
