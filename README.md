[real-python-discord-bot]: https://realpython.com/how-to-make-a-discord-bot-python/
[kline-stream-intervals]: https://bybit-exchange.github.io/docs/v5/websocket/public/kline
[rsi]: https://www.investopedia.com/terms/r/rsi.asp
[bybit]: https://www.bybit.com/en
[pgi]: https://discord.com/developers/docs/topics/gateway#gateway-intents
[pi]: https://discord.com/developers/docs/topics/gateway#presence-update
[smi]: https://discord.com/developers/docs/topics/gateway#list-of-intents
[mcp]: https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ
[ddp]: https://discord.com/developers/docs/intro


# DBTS Discord Bot
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

## Overview
DBTS Discord Bot connects to a Discord server, retrieves market data from [Bybit][bybit] using WebSocket, calculates the 
[Relative Strength Index (RSI)][rsi], and sends alerts to a specified Discord channel based on [RSI][rsi] thresholds.

## Requirements
- Docker (development version was: Docker version 20.10.23, build 7155243)
- Python 3.10.11 (recommended)

## Docker Setup

### Clone the repository:
```sh
git clone https://github.com/konfle/dbts.git
cd dbts
```

### Create a .env file in the root directory of the project and add the following environment variables:
It may be helpful to visit this [resource][real-python-discord-bot] in case of any trouble to get the Discord 
data needed for .env file.

Variables must be set are:
- DISCORD_TOKEN
- DISCORD_GUILD
- DISCORD_CHANNEL_ID

Optional variables are:
- SYMBOL (default is: SOLUSDT)
- INTERVAL (default is: 60)
- RSI_PERIOD (default is: 14)
```
DISCORD_TOKEN=<your_discord_bot_token>  # Discord bot token required to authenticate the bot with Discord servers.
DISCORD_GUILD=<your_discord_guild_name>  # Name of the Discord server (guild) where the bot will operate.
DISCORD_CHANNEL_ID=<your_discord_channel_id>  # ID of the Discord channel where the bot will send messages.
SYMBOL=SOLUSDT  # Symbol for the trading pair (e.g., SOL/USDT) for market data fetching.
INTERVAL=1  # Interval in minutes for fetching k-line data from Bybit (e.g., 1 for 1-minute intervals).
RSI_PERIOD=14  # Period in which to calculate the Relative Strength Index (RSI) based on closing prices.
```

### Build the Docker image:
```sh
docker build -t rsi-discord-bot .
```

### Run the Docker container:
```sh
docker run --env-file .env rsi-discord-bot
```

## Local Setup
To run this bot locally on your machine, follow these steps:

### Install Python 3.10.11:
Ensure you have Python 3.10.11 installed on your system. You can download it from
[Python's official website](https://www.python.org/downloads/release/python-31011/).

### Clone the repository:
```sh
git clone https://github.com/konfle/dbts.git
cd dbts
```

### Install required libraries:
Navigate to the project directory and install all required libraries using pip
```sh
pip install -r requirements.txt
```

### Run the bot:
```sh
python main.py
```

## Usage
The bot connects to the specified Discord server and channel. It fetches SOL/USDT k-line data from Bybit and calculates
the [RSI][rsi]. If the [RSI][rsi] is above 70 or below 30, it sends a message to the specified Discord channel.

### Commands
Most commands required that test mode is enabled.
- !rsi: Displays the current Relative Strength Index ([RSI][rsi]) based on the historical closing prices.
- !testmode True/False: Enables or disables test mode. In test mode, the bot simulates [RSI][rsi] alerts
without real market data.
- !testalert <rsi_value>: Sends a test [RSI][rsi] alert message to the Discord channel.
- !teststatus: Displays the current status of test mode.

### Tips
- Make sure you have access to the correct environment variables (`DISCORD_TOKEN`, `DISCORD_GUILD`, `DISCORD_CHANNEL_ID`).
- Test the code locally before running in the Docker container.
- Make sure you have the correct permissions for the bot on the Discord server.
- Make sure that bot has [Privileged Gateway Intents][pgi] ([PRESENCE INTENT][pi], 
[SERVER MEMBERS INTENT][smi], [MESSAGE CONTENT INTENT][mcp]) enabled on your [Discord Developers Platform][ddp]

### Troubleshooting

- RuntimeError: Event loop is closed

    Check bot [Privileged Gateway Intents][pgi] on your [Discord Developers Platform][ddp] are enabled.


- AttributeError: 'NoneType' object has no attribute 'send'

    Check bot [Privileged Gateway Intents][pgi] on your [Discord Developers Platform][ddp] are enabled.

### Resources
- [How to make a dicord bot with Python][real-python-discord-bot]
- [Relative Strength Index (RSI)][rsi]
- [Discord Developers Platform][ddp]
- [K-line stream intervals][kline-stream-intervals]
- [Bybit Documentation](https://bybit-exchange.github.io/docs/v5/intro)
- [Pybit](https://github.com/bybit-exchange/pybit?tab=readme-ov-file#about)
