import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
guild_name = discord.utils.get(client.guilds, name=GUILD)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord {guild_name}!')

client.run(TOKEN)
