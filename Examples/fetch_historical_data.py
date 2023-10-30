# External imports
from typing import Optional, Union

# Third-party imports
from pandas import DataFrame, Timestamp

# Local imports
from Historical_Data.crypto import CoingeckoFetcher
from Historical_Data.stock import AlpacaFetcher


def fetch_crypto(
    symbol: str, starting_date: Optional[Union[str, Timestamp]] = None
) -> DataFrame:
    """
    Fetch historical cryptocurrency data.

    Args:
        symbol (str): The symbol of the cryptocurrency.
        starting_date (Optional[Union[str, Timestamp]]): The starting date for data retrieval.

    Returns:
        DataFrame: A pandas DataFrame containing cryptocurrency data.

    Raises:
        Exception: If an error occurs during data fetching.

    Example usage:
    ```
    crypto_symbol = 'mantle'
    crypto_data = fetch_crypto(crypto_symbol)
    ```
    """
    fetcher = CoingeckoFetcher(symbol=symbol)
    if starting_date is None:
        starting_date = fetcher.get_earliest_price()
    data = fetcher.fetch_raw_data(start_date=starting_date)
    return data


def fetch_stock(
    symbol: str, starting_date: Optional[Union[str, Timestamp]] = None
) -> DataFrame:
    """
    Fetch historical stock data.

    Args:
        symbol (str): The symbol of the stock.
        starting_date (Optional[Union[str, Timestamp]]): The starting date for data retrieval.

    Returns:
        DataFrame: A pandas DataFrame containing stock data.

    Raises:
        Exception: If an error occurs during data fetching.

    Example usage:
    ```
    stock_symbol = 'tsla'
    stock_data = fetch_stock(stock_symbol)
    ```
    """
    fetcher = AlpacaFetcher(symbol=symbol)
    if starting_date is None:
        starting_date = fetcher.get_earliest_price()
    data = fetcher.fetch_raw_data(start_date=starting_date)
    return data


if __name__ == "__main__":
    stock_symbol = "tsla"
    crypto_symbol = "mantle"
    stock_data = fetch_stock(stock_symbol)
    crypto_data = fetch_crypto(crypto_symbol)
