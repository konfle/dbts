import os
import numpy as np
import asyncio
import logging
from pybit.unified_trading import WebSocket

from utils.logger_config import setup_logging
from config.settings import TOKEN, CHANNEL, SYMBOL, INTERVAL, RSI_PERIOD
from data.historical_data import get_historical_data, closes
from utils.rsi_calculator import calculate_rsi
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


async def send_discord_message(rsi):
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
    channel = bot.get_channel(CHANNEL)
    if channel:
        if rsi > 70:
            logger.debug(f"Sending message to channel: {channel}")
            await channel.send(f"RSI is over 70 - it's SELL time! RSI value: {rsi:.2f}")
        elif rsi < 30:
            logger.debug(f"Sending message to channel: {channel}")
            await channel.send(f"RSI is lower 30 - it's BUY time! RSI value: {rsi:.2f}")
    else:
        logger.warning("Channel not found.")


def handle_message(message):
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
            bot.loop.create_task(send_discord_message(latest_rsi))


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
        callback=handle_message
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
