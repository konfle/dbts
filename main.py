import os
import discord
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Get the Discord bot token and guild (server) name from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Set up the intents for the bot, specifically requesting permission to access member information
intents = discord.Intents.default()
intents.members = True

# Create a new Discord client instance with the specified intents
client = discord.Client(intents=intents)

# Define a variable to store the guild (server) object, which will be found later when the bot connects
guild_name = discord.utils.get(client.guilds, name=GUILD)


@client.event
async def on_ready():
    """
    Event handler that is called when the bot has successfully connected to Discord.

    This function prints a message to the console indicating that the bot has connected
    and specifies the name of the guild (server) it has connected to.
    """
    print(f'{client.user.name} has connected to Discord {guild_name}!')


@client.event
async def on_member_join(member):
    """
    Event handler that is called whenever a new member joins the guild (server).

    This function creates a direct message (DM) channel with the new member and sends
    them a welcome message.

    Parameters:
    member (discord.Member): The member who joined the guild.
    """
    # Create a direct message (DM) channel with the new member
    await member.create_dm()
    # Send a welcome message to the new member via DM
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to {guild_name} my Discord server!'
    )


# Start the bot using the token from the environment variables
client.run(TOKEN)
