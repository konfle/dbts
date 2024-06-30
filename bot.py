import discord
from discord.ext import commands

# Configuration of bot intents
intents = discord.Intents.all()
intents.members = True
intents.message_content = True


def create_bot():
    bot = commands.Bot(command_prefix="!", intents=intents)
    return bot
