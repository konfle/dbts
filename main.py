import os
import discord
import numpy as np
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from pybit.unified_trading import WebSocket

# Load environment variables from a .env file
load_dotenv()

# Get the Discord bot token and guild (server) name from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = int(os.getenv("DISCORD_CHANNEL_ID"))
SYMBOL = os.getenv("SYMBOL")
INTERVAL = int(os.getenv("INTERVAL"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD"))

# Set up the intents for the bot, specifically requesting permission to access member information
intents = discord.Intents.default()
intents.message_content = True  # Ensure this intent is enabled for command handling

# Create a new bot instance with the specified intents
bot = commands.Bot(command_prefix="!", intents=intents)

# List to store closing prices
closes = [131.52, 131.56, 131.57, 131.58, 131.56,
          131.42, 131.31, 131.27, 131.28, 131.28,
          131.28, 131.17, 131.19, 131.45]
test_mode = False


# Function for calculating RSI
def calculate_rsi(closes, period=RSI_PERIOD):
    """
    Calculate the Relative Strength Index (RSI) for a given series of closing prices.

    Parameters:
    - closes (list or np.array): List or array of closing prices.
    - period (int): Period for RSI calculation (default is RSI_PERIOD).

    Returns:
    - np.array: Array of RSI values corresponding to the input closing prices.

    RSI is a momentum oscillator that measures the speed and change of price movements.
    It oscillates between 0 and 100, with readings above 70 generally indicating overbought
    conditions and readings below 30 indicating oversold conditions.
    """
    deltas = np.diff(closes)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(closes)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(closes)):
        delta = deltas[i-1]  # difference between current and previous closing price
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period-1) + upval) / period
        down = (down * (period-1) + downval) / period

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


@bot.event
async def on_ready():
    """
    Event handler that is called when the bot has successfully connected to Discord.

    Returns:
        None

    This function retrieves the guild (server) information based on the predefined
    GUILD name from environment variables and prints a message to the console
    indicating that the bot has connected to Discord. It also initiates a connection
    to the WebSocket for receiving market data.
    """
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f"{bot.user.name} has connected to Discord {guild.name}!")

    # Start the WebSocket connection
    asyncio.ensure_future(connect_to_websocket())


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
    await bot.wait_until_ready()  # Ensure the bot is ready before getting the channel
    channel = bot.get_channel(CHANNEL)
    print(f"Sending message to channel: {channel}")  # Debugging line
    if channel:
        if rsi > 70:
            await channel.send(f"RSI is over 70 - it's SELL time!: {rsi}")
        elif rsi < 30:
            await channel.send(f"RSI is lower 30 - it's BUY time!: {rsi}")
    else:
        print("Channel not found.")


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
    print(f"Received message: {message}")  # Debugging line
    data = message["data"][0]
    if data['confirm']:  # If the candle is closed
        close_price = float(data["close"])
        print(f"Closed candle price: {close_price}")  # Debugging line
        closes.append(close_price)
        print(f"Current closes: {closes}")  # Debugging line

        if len(closes) > RSI_PERIOD:
            closes.pop(0)  # Keep only the last RSI_PERIOD closes

        if len(closes) >= RSI_PERIOD:
            rsi = calculate_rsi(np.array(closes))
            latest_rsi = rsi[-1]
            print(f"RSI: {latest_rsi}")
            # Use asyncio.run_coroutine_threadsafe to submit task to the event loop
            asyncio.run_coroutine_threadsafe(send_discord_message(latest_rsi), bot.loop)


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
    print("Connecting to WebSocket...")
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


# Command to toggle test mode
@bot.command(name="teststatus")
async def toggle_test_mode(ctx):
    """
    Toggles and displays the current test mode status.

    This command toggles the global `test_mode` variable between True and False based on
    the current state. It sends an embedded message to the Discord channel specified by
    `ctx` indicating whether test mode is currently enabled or disabled.

    Parameters:
    - ctx (commands.Context): The context object representing the invocation context
                              of the command in Discord.

    Returns:
        None
    """
    embed = discord.Embed(
        title="Test Mode Status",
        description=f"Test mode is currently {'enabled' if test_mode else 'disabled'}.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


# Command to toggle test mode
@bot.command(name="testmode")
async def toggle_test_mode(ctx, mode: bool):
    """
    Toggles the test mode setting and displays the updated status.

    This command allows toggling of the global `test_mode` variable between True and False
    based on the provided `mode` parameter. It sends an embedded message to the Discord
    channel specified by `ctx` indicating whether test mode has been enabled or disabled.

    Parameters:
    - ctx (commands.Context): The context object representing the invocation context
                              of the command in Discord.
    - mode (bool): The new test mode setting. True to enable test mode, False to disable it.

    Returns:
        None
    """
    global test_mode
    test_mode = mode
    if test_mode:
        embed = discord.Embed(
            title="Test Mode Updated",
            description="Test mode is now enabled.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="Test Mode Updated",
            description="Test mode is now disabled.",
            color=discord.Color.red()
        )
    await ctx.send(embed=embed)


# Command to send a manual RSI alert
@bot.command(name="testalert")
async def send_test_alert(ctx, rsi: float):
    """
    Sends a test alert message to the Discord channel if test mode is enabled.

    This command checks if `test_mode` is True. If it is, it sends a Discord message
    indicating the RSI value provided as `rsi` and also sends an embedded message confirming
    that the test alert has been sent. If `test_mode` is False, it sends an embedded message
    informing the user that test mode is not enabled and provides instructions on how to
    enable it.

    Parameters:
    - ctx (commands.Context): The context object representing the invocation context
                              of the command in Discord.
    - rsi (float): The RSI value to be included in the test alert message.

    Returns:
        None
    """
    if test_mode:
        await send_discord_message(rsi)
        embed = discord.Embed(
            title="Test Alert Sent",
            description=f"Test alert sent with RSI value: {rsi}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Current RSI",
            description=f"Test mode is not enabled. Use !testmode True to enable test mode.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


# Command to show the current RSI
@bot.command(name='rsi')
async def show_rsi(ctx):
    """
    Displays the current Relative Strength Index (RSI) in a Discord embedded message.

    If test mode is enabled (`test_mode` is True), this command calculates the RSI based on
    the historical closing prices stored in `closes`. If there are enough data points
    (at least `RSI_PERIOD`), it calculates the RSI and sends an embedded message with the
    calculated RSI value. If there are not enough data points, it sends an embedded message
    indicating that there is insufficient data to calculate the RSI.

    If test mode is not enabled (`test_mode` is False), it sends an embedded message
    informing the user that test mode is not enabled and provides instructions on how to
    enable it.

    Parameters:
    - ctx (commands.Context): The context object representing the invocation context
                              of the command in Discord.

    Returns:
        None
    """
    if test_mode:
        if len(closes) >= RSI_PERIOD:
            rsi = calculate_rsi(np.array(closes))
            latest_rsi = rsi[-1]
            embed = discord.Embed(
                title="Current RSI",
                description=f"The current RSI is: {latest_rsi}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Current RSI",
                description=f"Not enough data to calculate RSI. Current closes: {len(closes)}",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Current RSI",
            description=f"Test mode is not enabled. Use command: !testmode True to enable test mode.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


# Start the bot
async def main():
    """
    Main entry point to start the Discord bot.

    This function prints a message indicating that the bot is starting, then starts
    the bot using the provided bot token (`TOKEN`). Once the bot is successfully started,
    it prints a message confirming that the bot has started.

    Parameters:
        None

    Returns:
        None
    """
    print("Bot is starting...")
    await bot.start(TOKEN)
    print("Bot has started.")

if __name__ == "__main__":
    # Print a message indicating the start of bot and WebSocket initialization
    print("Starting bot and WebSocket...")

    # Schedule the execution of the main asynchronous function `main` using asyncio
    asyncio.ensure_future(main())

    # Run the event loop indefinitely to keep the program running
    asyncio.get_event_loop().run_forever()
