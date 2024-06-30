import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
CHANNEL = int(os.getenv("DISCORD_CHANNEL_ID"))
SYMBOL = os.getenv("SYMBOL", "SOLUSDT")
INTERVAL = int(os.getenv("INTERVAL", 60))  # Jest liczony w minutach
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
