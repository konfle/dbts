import os
import logging
from dotenv import load_dotenv

from utils.logger_config import setup_logging

# Configuration of logging
logger = logging.getLogger(__name__)

# Load environment variables from a .env file
load_dotenv()

# Get the Discord bot token and guild (server) name from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = int(os.getenv("DISCORD_CHANNEL_ID"))

if TOKEN is None or GUILD is None or CHANNEL is None:
    logger.error("DISCORD_TOKEN, DISCORD_GUILD, and DISCORD_CHANNEL_ID must be set in the .env file.")
    exit(1)

# Set default values for SYMBOL, INTERVAL, and RSI_PERIOD
SYMBOL = os.getenv("SYMBOL", "SOLUSDT")
INTERVAL = int(os.getenv("INTERVAL", 60))  # It's counted in minutes
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
