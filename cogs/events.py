import logging
import discord
from discord.ext import commands
from config.settings import GUILD

# Configuration of logging
logger = logging.getLogger(__name__)


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event handler that is called when the bot has successfully connected to Discord.
        """
        guild = discord.utils.get(self.bot.guilds, name=GUILD)
        logger.info(f"{self.bot.user.name} has connected to Discord {guild.name}!")


async def setup(bot):
    await bot.add_cog(EventCog(bot))
