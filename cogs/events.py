import logging
import discord
import numpy as np

from discord.ext import commands

from config.settings import GUILD, CHANNEL, RSI_PERIOD
from data.historical_data import closes
from utils.rsi_calculator import calculate_rsi

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

    async def send_discord_message(self, rsi):
        """
        Asynchronously sends a message to a Discord channel based on the current RSI value.

        Parameters:
        - rsi (float): The current RSI value to be evaluated.

        Returns:
            None

        This function waits until the Discord bot is ready before attempting to fetch the
        channel by its ID from the environment variables. It then sends a message to the
        channel indicating whether the RSI is considered high (over 70, indicating it's
        time to sell) or low (under 30, indicating it's time to buy).
        """
        channel = self.bot.get_channel(CHANNEL)
        if channel:
            if rsi > 70:
                logger.debug(f"Sending message to channel: {channel}")
                await channel.send(f"RSI is over 70 - it's SELL time! RSI value: {rsi:.2f}")
            elif rsi < 30:
                logger.debug(f"Sending message to channel: {channel}")
                await channel.send(f"RSI is lower 30 - it's BUY time! RSI value: {rsi:.2f}")
        else:
            logger.warning("Channel not found.")

    def handle_message(self, message):
        """
            Processes a message received from WebSocket for handling candlestick data.

            This function prints debug information about the received message and extracts
            the necessary data from it to update the list of closing prices (`closes`). If
            the candlestick data confirms the closing of a candle, it calculates the RSI
            based on the updated closing prices and sends a Discord message using the
            `send_discord_message` function.

            Args:
                message (dict): The message received from WebSocket containing candlestick data.

            Returns:
                None

            Debugging Lines:
            - Prints the received message.
            - Prints the closed candle price.
            - Prints the current list of closing prices.

            Notes:
            - Uses the global variables `closes` and `RSI_PERIOD` to store closing prices and
              calculate RSI.
            - Utilizes `asyncio.run_coroutine_threadsafe` to safely submit the `send_discord_message`
              coroutine to the event loop for sending Discord messages asynchronously.
        """
        logger.debug(f"Received message: {message}")
        data = message["data"][0]
        if data['confirm']:  # If the candle is closed
            close_price = float(data["close"])
            logger.debug(f"Closed candle price: {close_price}")
            closes.append(close_price)
            logger.debug(f"Current closes: {closes}")

            if len(closes) > RSI_PERIOD:
                closes.pop(0)  # Keep only the last RSI_PERIOD closes

            if len(closes) >= RSI_PERIOD:
                rsi = calculate_rsi(np.array(closes))
                latest_rsi = rsi[-1]
                logger.info(f"RSI calculated: {latest_rsi:.2f}")
                # Use asyncio.run_coroutine_threadsafe to submit task to the event loop
                self.bot.loop.create_task(self.send_discord_message(latest_rsi))


async def setup(bot):
    await bot.add_cog(EventCog(bot))
