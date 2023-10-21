"""
This module fetches stock data from Alpaca.

Standard Library Imports:
- datetime: Provides classes for manipulating dates and times.
- os: Provides a way of using operating system dependent functionality.
- time: Provides various time-related functions.

Third-Party Library Imports:
- numpy: The fundamental package for array computing with Python.
- pandas: An easy-to-use open source data analysis and manipulation tool.
- pytz: World timezone definitions, modern and historical.
- dotenv: Reads the key-value pair from .env file and adds them to environment variable.
- halo: Beautiful terminal spinners in Python.
- pandas_market_calendars: Provides market calendars using the pandas library.

External Library Imports:
- alpaca.data.historical: Fetches historical data from Alpaca.
- alpaca.data.requests: Handles requests to Alpaca.
- alpaca.data.timeframe: Handles timeframes for Alpaca data.

Custom Module Imports:
- Historical_Data.log_config: Custom logging configuration.

Classes:
- Spinner: Class for loading animations.
- AlpacaFetcher: Class to fetch stock data from Alpaca.

Functions:
- use_symbol: Decorator function to handle symbol input.
"""


# Standard Library Imports
import datetime
import os
import time

# Third-Party Library Imports
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import pytz

# External Library Imports
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv
from halo import Halo

from Historical_Data.log_config import logger
from Historical_Data.pre_processor import preprocess_dataframe

# Custom Module Imports
from Historical_Data.validator import validate_dataframe


def use_symbol(func):
    """
    Decorator function to handle symbol input.

    Parameters:
    - func: The function to be decorated.

    Returns:
    - The decorated function.
    """

    def wrapper(self, symbol=None, *args, **kwargs):
        if symbol is None:
            symbol = self.symbol.upper()
        else:
            symbol = symbol.upper()
        return func(self, symbol, *args, **kwargs)

    return wrapper


class Spinner:
    """
    Class for loading animations.

    Attributes:
    - spinner: A list of spinner symbols.
    - delay: The delay between each symbol in the spinner animation.

    Methods:
    - __init__(self, delay: float = 0.1): Initializes the Spinner object with a delay.
    - __enter__(self): Starts the spinner animation.
    - spinner_function(self): Generates the spinner animation symbols.
    - __exit__(self, exc_type, exc_val, exc_tb): Stops the spinner animation.
    """

    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, delay: float = 0.1):
        self.delay = delay

    def __enter__(self):
        self.spinner_generator = self.spinner_function()
        next(self.spinner_generator)

    # Function to generate spinner animation
    def spinner_function(self):
        while True:
            for symbol in self.spinner:
                yield symbol
                time.sleep(self.delay)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\r ", end="", flush=True)


class AlpacaFetcher:
    """
    Class to fetch stock data from Alpaca.

    Attributes:
    - CATEGORY: The category of the stock data.
    - SOURCE: The source of the stock data.
    - client: The Alpaca StockHistoricalDataClient object.
    - symbol: The symbol of the stock.

    Methods:
    - __init__(self, symbol: str): Initializes the AlpacaFetcher object with a symbol.
    - get_earliest_price(self, symbol: str) -> str: Returns the earliest price date for the stock.
    - is_market_open(self, start_date: datetime.datetime, end_date: datetime.datetime) -> bool:
        Checks if the market is open.
    - fetch_raw_data(self, symbol: str, start_date: datetime.datetime) -> pd.DataFrame:
        Fetches raw stock data.
    """

    CATEGORY = "stock"
    SOURCE = "alpaca"

    def __init__(self, symbol: str):
        load_dotenv()
        self.client = StockHistoricalDataClient(
            api_key=os.environ.get("ALPACA_API_KEY"),
            secret_key=os.environ.get("ALPACA_SECRET_KEY"),
        )
        self.symbol = symbol.upper()

    @use_symbol
    def get_earliest_price(self, symbol: str) -> str:
        return "2010-01-01 00:00:00"  # Alpaca only supports 7yr 1hr data

    # Function to check if the market is open
    def is_market_open(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> bool:
        # get the NASDAQ calendar
        nasdaq = mcal.get_calendar("NASDAQ")

        # Create a date range with hourly frequency
        date_range = pd.date_range(
            start=start_date, end=end_date, freq="H", tz=pytz.utc
        )

        for date in date_range:
            # Check if the current hour is outside of market hours
            schedule = nasdaq.schedule(start_date=date.date(), end_date=date.date())
            if not schedule.empty:
                market_open_utc = schedule.iloc[0]["market_open"].tz_convert(pytz.utc)
                market_close_utc = schedule.iloc[0]["market_close"].tz_convert(pytz.utc)
                if (date > market_open_utc and date < market_close_utc) and (
                    np.datetime64(date) not in nasdaq.holidays().holidays
                ):
                    return True
        return False

    @use_symbol
    # Function to fetch raw stock data
    def fetch_raw_data(
        self, symbol: str, start_date: datetime.datetime
    ) -> pd.DataFrame:
        end_date = pd.to_datetime(pd.Timestamp.utcnow()).replace(
            tzinfo=None
        ) - datetime.timedelta(minutes=16)
        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Hour,
            start=start_date,
            end=end_date,
            adjustment="all",
        )
        if self.is_market_open(start_date, end_date):
            try:
                spinner = Halo(
                    text=f"Downloading {symbol} stock data...", spinner="line"
                )
                spinner.start()

                bars = self.client.get_stock_bars(request_params)
                spinner.stop()
                df = bars.df
                logger.success(f"Finished Fetching {symbol} stock data!")

                df = df.reset_index()
                df["source"] = self.SOURCE
                df["category"] = self.CATEGORY
                df = df.drop(columns=["trade_count", "vwap"], axis=1)
                df = preprocess_dataframe(df)

                if validate_dataframe(df):
                    return df
                else:
                    raise ValueError

            except KeyError as e:
                logger.error(f"KeyError for stock {symbol}: {e}")
                return pd.DataFrame()
        else:
            logger.warning(f"Market is closed for {symbol} stock")
            return pd.DataFrame()
