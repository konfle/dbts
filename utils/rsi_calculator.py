import ta
import pandas as pd

from config.settings import RSI_PERIOD


# Function for calculating RSI using Technical Analysis Library
def calculate_rsi(closes, period=RSI_PERIOD):
    """
    Calculate the Relative Strength Index (RSI) for a given series of closing prices using Technical Analysis Library.

    Parameters:
    - closes (list or np.array): List or array of closing prices.
    - period (int): Period for RSI calculation (default is RSI_PERIOD).

    Returns:
    - np.array: Array of RSI values corresponding to the input closing prices.

    RSI is a momentum oscillator that measures the speed and change of price movements.
    It oscillates between 0 and 100, with readings above 70 generally indicating overbought
    conditions and readings below 30 indicating oversold conditions.
    """
    df = pd.DataFrame(closes, columns=["close"])
    rsi = ta.momentum.RSIIndicator(df["close"], window=period).rsi()
    return rsi.values
