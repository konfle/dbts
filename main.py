import os
import asyncio
import logging

from pybit.unified_trading import WebSocket

from utils.logger_config import setup_logging
from config.settings import TOKEN, SYMBOL, INTERVAL
from data.historical_data import get_historical_data
from bot import create_bot


# Configure logger
setup_logging()
logger = logging.getLogger(__name__)

# Initialization bot instance
bot = create_bot()


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")


# WebSocket configuration and management
async def connect_to_websocket():
    """
    Connects to the WebSocket and starts streaming candlestick data.

    This function initializes a WebSocket connection using the `pybit.unified_trading.WebSocket`
    class with testnet enabled and linear channel type. It then starts streaming candlestick data
    for a specified symbol and interval, using the `handle_message` function as the callback.

    Returns:
        None

    Notes:
    - Uses global variables `INTERVAL` and `SYMBOL` to configure the WebSocket stream parameters.
    - Runs indefinitely to keep the WebSocket connection alive, sleeping for 1 second between iterations.
    """
    logger.info("Connecting to WebSocket...")
    ws = WebSocket(
        testnet=True,
        channel_type="linear",
    )
    ws.kline_stream(
        interval=INTERVAL,
        symbol=SYMBOL,
        callback=bot.get_cog("EventCog").handle_message
    )
    # Keep the WebSocket running
    while True:
        await asyncio.sleep(1)


# Start the bot
async def main():
    """
    Main entry point to start the Discord bot.

    This function prints a message indicating that the bot is starting, then starts
    the bot using the provided bot token (`TOKEN`). Once the bot is successfully started,
    it prints a message confirming that the bot has started.

    Returns:
        None
    """
    logger.info("Fetching historical data...")
    get_historical_data()
    logger.info("Bot is starting...")
    bot_task = asyncio.create_task(bot.start(TOKEN))
    logger.info("Bot has started.")
    await load_cogs()
    logger.info("Starting WebSocket...")
    websocket_task = asyncio.create_task(connect_to_websocket())
    logger.info("WebSocket has started.")
    await asyncio.gather(bot_task, websocket_task)

if __name__ == "__main__":
    logger.info("Starting bot and WebSocket...")
    asyncio.run(main())
