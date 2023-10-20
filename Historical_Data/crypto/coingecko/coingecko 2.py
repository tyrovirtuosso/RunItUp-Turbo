"""
This module fetches crypto data from Coingecko.

Imports:
- datetime: Module for manipulating dates and times.
- time: Module for time-related functions.
- List from typing: Type hint for a list.
- pandas as pd: Library for data manipulation
and analysis.
- requests: Library for making HTTP requests.
- termcolor from termcolor: Library for
printing colored text.
- tqdm from tqdm: Library for creating
progress bars.

Custom Modules:
- log_config from Historical_Data.log_config:
Custom module for configuring logging.
- vpn_utils from Historical_Data.vpn_utils:
Custom module for VPN-related utilities.

Class: CoingeckoFetcher
- __init__(self, symbol: str): Constructor method
that initializes the CoingeckoFetcher object
with a symbol parameter.
- get_earliest_price(self, symbol: str) ->
datetime.datetime: Retrieves the earliest price
date for a given symbol.
- date_ranges(self, start_date: datetime.datetime,
end_date: datetime.datetime): Generates date
ranges between start_date and end_date with
a 90-day interval.
- construct_request_url(self, symbol: str,
start_date: datetime.datetime,
end_date: datetime.datetime) -> str: Constructs
the request URL for fetching historical data.
- extract_data_from_response(self, data: dict) ->
pd.DataFrame: Extracts data from the API
response and returns it as a DataFrame.
- make_api_request(self, url: str) -> pd.DataFrame:
Makes an API request and retrieves historical
data.
- activate_vpn(self) -> bool: Activates a VPN
connection and returns True if the connection
is successful.
- fetch_raw_data(self, symbol: str, start_date:
datetime.datetime) -> pd.DataFrame: Fetches raw
data for a given symbol and date range and
combines it into a single DataFrame.
- handle_connect_timeout(self): Handles a
connection timeout error.
- handle_http_error(self, err: Exception):
Handles HTTP errors.

Please note that the code relies on custom modules
(log_config and vpn_utils) and external libraries
(pandas, requests, termcolor, tqdm). The documentation
for these modules and libraries is not provided in
the code snippet.
"""

# Standard Library Imports
import datetime
import time

# Third-Party Library Imports
import pandas as pd
import requests
from termcolor import colored
from tqdm import tqdm

# Custom Module Imports
from Historical_Data.log_config import logger
from Historical_Data.vpn_utils import (
    get_current_ip,
    is_ping_successful,
    vpn_connect,
    vpn_disconnect,
)


# Define a decorator to handle the 'symbol' parameter
def use_symbol(func):
    """
    Decorator that converts the 'symbol' parameter to lowercase if provided.

    Args:
        func (callable): The function to be wrapped.

    Returns:
        callable: The wrapped function.
    """

    def wrapper(self, symbol=None, *args, **kwargs):
        if symbol is None:
            symbol = self.symbol.lower()
        else:
            symbol = symbol.lower()
        return func(self, symbol, *args, **kwargs)

    return wrapper


class CoingeckoFetcher:
    CATEGORY = "crypto"
    SOURCE = "coingecko"

    def __init__(self, symbol: str):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.symbol = symbol.lower()

    @use_symbol
    def get_earliest_price(self, symbol: str) -> datetime.datetime:
        """
        Get the earliest price date for a given symbol.

        Args:
            symbol (str): The symbol to retrieve the earliest price for.

        Returns:
            datetime.datetime: The earliest price date.
        """
        try:
            url = f"https://coins.llama.fi/prices/first/coingecko:{symbol}"
            response = requests.get(url)
            timestamp = response.json()["coins"][f"coingecko:{symbol}"]["timestamp"]
            return pd.to_datetime(timestamp, unit="s")
        except requests.exceptions.ConnectTimeout:
            self.handle_connect_timeout()
        except KeyError:
            message = f"There is no {symbol} symbol in Coingecko API name"
            logger.error(message)
            return None

    def date_ranges(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        Generate date ranges between start_date and end_date with a 90-day interval.

        Args:
            start_date (datetime.datetime): The start date.
            end_date (datetime.datetime): The end date.

        Yields:
            Tuple[datetime.datetime, datetime.datetime]:
            A tuple with start and end dates for each interval.
        """
        days = (end_date - start_date).days
        num_requests = days // 90 + 1

        for i in range(num_requests):
            current_start = start_date + datetime.timedelta(days=i * 90)
            current_end = min(
                start_date + datetime.timedelta(days=(i + 1) * 90), end_date
            )
            yield current_start, current_end

    @use_symbol
    def construct_request_url(
        self, symbol: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> str:
        """
        Construct the request URL for fetching historical data.

        Args:
            symbol (str): The symbol.
            start_date (datetime.datetime): Start date.
            end_date (datetime.datetime): End date.

        Returns:
            str: The constructed URL.
        """

        return (
            f"{self.base_url}/coins/{symbol}/market_chart/range?vs_currency=usd&from="
            f"{int(start_date.timestamp())}&to={int(end_date.timestamp())}"
            f"?cache-bust={str(time.time())}"
        )

    def extract_data_from_response(self, data: dict) -> pd.DataFrame:
        """
        Extract data from the API response.

        Args:
            data (dict): API response data.

        Returns:
            pd.DataFrame: Processed data as a DataFrame.
        """
        timestamps = pd.to_datetime([x[0] for x in data["prices"]], unit="ms")
        prices = [x[1] for x in data["prices"]]
        total_volumes = [x[1] for x in data["total_volumes"]]
        return pd.DataFrame(
            {
                "close": prices,
                "open": prices,
                "high": prices,
                "low": prices,
                "volume": total_volumes,
            },
            index=timestamps,
        )

    def make_api_request(self, url: str) -> pd.DataFrame:
        """
        Make an API request and retrieve historical data.

        Args:
            url (str): The API request URL.

        Returns:
            pd.DataFrame: Historical data.
        """
        while True:
            try:
                logger.info(f"Making API request with IP:{get_current_ip()}")
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                return self.extract_data_from_response(data)
            except Exception as e:
                logger.warning(e)
                self.activate_vpn()
                logger.success("Exited Exception")

    def activate_vpn(self) -> bool:
        """
        Activate a VPN connection.

        Returns:
            bool: True if VPN connection is successful, otherwise False.
        """
        sleep_time = 5
        logger.info(f"In activate_vpn, sleeping for {sleep_time}")
        time.sleep(sleep_time)
        connected = False
        while not connected:
            try:
                vpn_disconnect()
                vpn_connect()
                if is_ping_successful():
                    connected = True
                    logger.success("Pinged Successfully!")
            except Exception as e:
                logger.warning(e)
                vpn_disconnect()
                vpn_connect()
        return connected

    @use_symbol
    def fetch_raw_data(
        self, symbol: str, start_date: datetime.datetime
    ) -> pd.DataFrame:
        """
        Fetch raw data for a given symbol and date range and combine it into a single DataFrame.

        Args:
            symbol (str): The symbol.
            start_date (datetime.datetime): Start date.

        Returns:
            pd.DataFrame: Combined DataFrame of raw data.
        """
        logger.info(f"Initiated Data Fetching for symbol {symbol} from {start_date}")
        raw_data = []
        end_date = pd.to_datetime(pd.Timestamp.utcnow()).replace(tzinfo=None)
        start_date = start_date.replace(minute=0, second=0, microsecond=0)
        end_date = end_date.replace(minute=0, second=0, microsecond=0)

        # Calculate the total number of API requests
        num_requests = (end_date - start_date).days // 90 + 1
        logger.info(f"Number of requests:{num_requests}")

        # Use tqdm to add a progress bar to the loop, and format the output string
        for i, (current_start, current_end) in tqdm(
            enumerate(self.date_ranges(start_date, end_date)),
            desc=colored(f"Fetching {symbol} data", "green"),
            unit="request",
            total=num_requests,
            bar_format="{desc}: {n}/{total} requests |{bar}| {percentage:3.0f}%",
        ):
            logger.info(f"Fetching Raw Data of {symbol}: {i}/{num_requests}")
            url = self.construct_request_url(symbol, current_start, current_end)
            data = self.make_api_request(url)
            data["symbol"] = symbol
            raw_data.append(data)

        vpn_disconnect()

        if raw_data is not None:
            combined_data = pd.concat(raw_data, ignore_index=False)
            combined_data = combined_data.rename_axis("timestamp")
            logger.success(f"Data for symbol {symbol} fetched successfully!")
            return combined_data
        logger.warning(f"Data for symbol {symbol} is None")
        return pd.DataFrame()

    def handle_connect_timeout(self):
        sleep_time = 10
        logger.error(
            f"Connection to api.coingecko.com timed out... Sleeping for {sleep_time} seconds"
        )
        time.sleep(sleep_time)

    def handle_http_error(self, err: Exception):
        if err.response.status_code == 429:
            time.sleep(2)
            vpn_connect()
        elif err.response.status_code == 503:
            time.sleep(10)
        else:
            raise err
