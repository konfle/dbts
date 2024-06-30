import logging

from pybit.unified_trading import HTTP
from datetime import datetime

from config.settings import RSI_PERIOD, INTERVAL, SYMBOL
from utils.logger_config import setup_logging


# Configuration of logging
logger = logging.getLogger(__name__)

closes = []


# Function to get historical data
def get_historical_data():
    """
    Fetches historical candlestick data for the given symbol and interval
    and populates the 'closes' list with closing prices.

    This function uses the pybit HTTP client to retrieve candlestick data.
    """
    session = HTTP(testnet=True)
    end_time = int(datetime.now().timestamp() * 1000)  # current time in milliseconds
    start_time = end_time - (RSI_PERIOD * INTERVAL * 60 * 1000)  # start time in milliseconds

    response = session.get_kline(
        category="inverse",
        symbol=SYMBOL,
        interval=INTERVAL,
        start=start_time,
        end=end_time,
    )

    if response["retCode"] == 0:
        logger.info("Successfully fetched historical data.")
        for entry in response["result"]["list"]:
            closes.append(float(entry[4]))  # Append the close price to closes
    else:
        logger.error(f"Error fetching historical data: {response['retMsg']}")
