[real-python-discord-bot]: https://realpython.com/how-to-make-a-discord-bot-python/
[kline-stream-intervals]: https://bybit-exchange.github.io/docs/v5/websocket/public/kline
[rsi]: https://www.investopedia.com/terms/r/rsi.asp
[bybit]: https://www.bybit.com/en
[pgi]: https://discord.com/developers/docs/topics/gateway#gateway-intents
[pi]: https://discord.com/developers/docs/topics/gateway#presence-update
[smi]: https://discord.com/developers/docs/topics/gateway#list-of-intents
[mcp]: https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ
[ddp]: https://discord.com/developers/docs/intro
[ta]: https://pypi.org/project/ta/
[minikube]: https://minikube.sigs.k8s.io/docs/


# DBTS - Discord Bot for RSI Alerts
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

## Overview
This project is a Discord bot that provides real-time [Relative Strength Index (RSI)][rsi] alerts for cryptocurrency 
trading. The bot fetches historical candlestick data from [Bybit][bybit] using WebSocket and REST API and calculates 
the [RSI][rsi] using the [Technical Analysis Library][ta]. It sends alerts to a specified Discord channel when the 
[RSI][rsi] indicates potential buy or sell opportunities.

## Requirements
- Docker (development version was: Docker version 20.10.23, build 7155243)
- Python 3.10.11 (recommended)

## Features
- Real-time [RSI][rsi] Calculation: Fetches real-time candlestick data and calculates [RSI][rsi] using the
[Technical Analysis Library][ta].

- Customizable Parameters: Configure the cryptocurrency symbol, time interval, and [RSI][rsi] period through environment
variables.

- Discord Alerts: Sends notifications to a Discord channel when [RSI][rsi] crosses the buy (below 30) or sell
(above 70) thresholds.

- WebSocket Integration: Continuously receives and processes market data via WebSocket.

## Setup and Installation
You can set up and run the bot using either Docker or a local Python environment. Follow the instructions for your 
preferred method:

### Option 1: Docker Setup

#### Clone the repository:
```sh
git clone https://github.com/konfle/dbts.git
cd dbts
```

#### Create a .env file in the root directory of the project and add the following environment variables:
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
DISCORD_GUILD='<your_discord_guild_name>'  # Name of the Discord server (guild) where the bot will operate.
DISCORD_CHANNEL_ID=<your_discord_channel_id>  # ID of the Discord channel where the bot will send messages.
SYMBOL=SOLUSDT  # Symbol for the trading pair (e.g., SOL/USDT) for market data fetching.
INTERVAL=1  # Interval in minutes for fetching k-line data from Bybit (e.g., 1 for 1-minute intervals).
RSI_PERIOD=14  # Period in which to calculate the Relative Strength Index (RSI) based on closing prices.
```

#### Build the Docker image:
```sh
docker build -t rsi-discord-bot .
```

#### Run the Docker container:
```sh
docker run --env-file .env rsi-discord-bot
```

### Option 2: Local Setup
To run this bot locally on your machine, follow these steps:

#### Clone the repository:
```sh
git clone https://github.com/konfle/dbts.git
cd dbts
```

#### Install required libraries:
Navigate to the project directory and install all required libraries using pip
```sh
pip install -r requirements.txt
```

#### Create and configure the `.env` file with your environment variables (as in Option 1)

#### Run the bot:
```sh
python main.py
```

### Option 3: Kubernetes Cluster Setup
To run this bot on the cluster (steps for local cluster setted up via [Minikube][minikube]) on your local machine, 
follow these steps:

#### Clone the repository:
```sh
git clone https://github.com/konfle/dbts.git
cd dbts
```

#### Build Docker image:
This setup ([bot deployment](k8s/dbts_deployment.yaml)) required Docker image to run this bot to create such image use command below.
```sh
docker build -t my-discord-bot:latest .
```

#### Start local cluster:
```sh
minikube start
```

#### Load bot Docker image to the Minikube cluster:
```sh
minikube image load my-discord-bot:latest
```

#### Create Kubernetes resources:
This bot required three resources for running:
- [Secret](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

Manifests for those resources are stored in directory k8s.

##### Secret
The secret manifest is the only one that required additional effort before creating while this resource storing
confidential data. Data stored in this resource are same data as in the .env file. To the nature of this resource data
must be base64 encoded. To achieve this you can use [this](https://www.base64encode.org/) web application.


```yaml
# dbts_secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: dbts
type: Opaque
data:
  DISCORD_TOKEN: <base64_your_discord_bot_token>
  DISCORD_GUILD: <base64_your_discord_guild_name>
  DISCORD_CHANNEL_ID: <base64_your_discord_channel_id>
  SYMBOL: U09MVVNEVA==
  INTERVAL: MQ==
  RSI_PERIOD: MTQ=
```

Create K8s Secret
```sh
kubectl create -f .\k8s\dbts_secret.yaml
```

Create K8s Deployment
```sh
kubectl create -f .\k8s\dbts_deployment.yaml
```

Create K8s Service
```sh
kubectl create -f .\k8s\dbts_service.yaml
```

##### Check that all resources are up and running:
```sh
kubectl get service,deployment,secret,pod
```

Example output from command above:
```sh
NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/dbts-service       NodePort    10.98.204.227   <none>        80:30001/TCP   4d

NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/dbts-deployment   1/1     1            1           4d

NAME                          TYPE     DATA   AGE
secret/dbts                   Opaque   6      4d

NAME                                   READY   STATUS    RESTARTS      AGE
pod/dbts-deployment-56b868767b-fwc87   1/1     Running   2 (30m ago)   4d
```
## Usage
The bot connects to the specified Discord server and channel. It fetches configured symbol (SOL/USDT by default) k-line 
data from [Bybit][bybit] and calculates the [RSI][rsi]. If the [RSI][rsi] is above 70 or below 30, it sends a message to
the specified Discord channel.

### Commands
Most commands required that test mode is enabled.
- !rsi: Displays the current Relative Strength Index ([RSI][rsi]) based on the historical closing prices.
- !testmode True/False: Enables or disables test mode. In test mode, the bot simulates [RSI][rsi] alerts
without real market data.
- !testalert <rsi_value>: Sends a test [RSI][rsi] alert message to the Discord channel.
- !teststatus: Displays the current status of test mode.

## Tips
- Make sure you have access to the correct environment variables (`DISCORD_TOKEN`, `DISCORD_GUILD`, `DISCORD_CHANNEL_ID`).
- Test the code locally before running in the Docker container.
- Make sure you have the correct permissions for the bot on the Discord server.
- Make sure that bot has [Privileged Gateway Intents][pgi] ([PRESENCE INTENT][pi], 
[SERVER MEMBERS INTENT][smi], [MESSAGE CONTENT INTENT][mcp]) enabled on your [Discord Developers Platform][ddp]

## Troubleshooting

- RuntimeError: Event loop is closed

    Check bot [Privileged Gateway Intents][pgi] on your [Discord Developers Platform][ddp] are enabled.


- AttributeError: 'NoneType' object has no attribute 'send'

    Check bot [Privileged Gateway Intents][pgi] on your [Discord Developers Platform][ddp] are enabled.

## Resources
- [How to make a dicord bot with Python][real-python-discord-bot]
- [Relative Strength Index (RSI)][rsi]
- [Discord Developers Platform][ddp]
- [K-line stream intervals][kline-stream-intervals]
- [Bybit Documentation](https://bybit-exchange.github.io/docs/v5/intro)
- [Discord Cogs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html)
- [Minikube][minikube]
- [Pybit](https://github.com/bybit-exchange/pybit?tab=readme-ov-file#about)

## License
This project is licensed under the MIT License.
