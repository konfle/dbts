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


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to {guild_name} my Discord server!'
    )

client.run(TOKEN)
