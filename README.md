# DBTS Discord Bot

## Requirements
- Docker

## Setup

### Clone the repository:
```sh
git clone https://github.com/yourusername/dbts.git
cd dbts
```

### Create a .env file in the root directory of the project and add the following environment variables:
```
DISCORD_TOKEN=<your_discord_bot_token>
DISCORD_GUILD=<your_discord_guild_name>
DISCORD_CHANNEL_ID=<your_discord_channel_id>
SYMBOL=SOLUSDT
INTERVAL=1
RSI_PERIOD=14
```

### Build the Docker image:
```
docker build -t rsi-discord-bot .
```

### Run the Docker container:
```
docker run --env-file .env rsi-discord-bot
```

## Usage
The bot will connect to the specified Discord server and channel. It will fetch SOL/USDT k-line data from Bybit and 
calculate the RSI. If the RSI is over 70 or below 30, it will send a message to the specified Discord channel.

### Tips
- Make sure you have access to the correct environment variables (`DISCORD_TOKEN`, `DISCORD_GUILD`, `DISCORD_CHANNEL_ID`).
- Test the code locally before running in the Docker container.
- Make sure you have the correct permissions for the bot on the Discord server.