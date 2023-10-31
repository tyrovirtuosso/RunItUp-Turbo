# Standard Library Imports
import datetime
import warnings
from typing import List, Union

# Third-Party Library Imports
import numpy as np
import pandas as pd

# Imports for Historical Data Handling (Crypto and Stock)
from Historical_Data.crypto import CoingeckoFetcher
from Historical_Data.stock import AlpacaFetcher

# Custom Logger Import
from log_config import logger

SUPPORTED_CATEGORIES: List[str] = ["crypto", "stock"]


def validate_category(category: str, symbol: str) -> None:
    """
    Validates if the category is supported.
    Args:
        category (str): The category to validate.
        symbol (str): The symbol associated with the category.
    Raises:
        ValueError: If the category is not supported.
    """
    if category.lower() not in SUPPORTED_CATEGORIES:
        error_message = (
            f"\033[93mUnsupported symbol-category: ({symbol}, {category})\033[0m"
        )
        logger.error(error_message)
        raise ValueError(error_message)


def get_fetcher(category: str, symbol: str) -> Union[CoingeckoFetcher, AlpacaFetcher]:
    """
    Get the appropriate data fetcher based on the category and symbol.

    Args:
        category (str): The category of the data ('crypto' or 'stock').
        symbol (str): The symbol to fetch data for.

    Returns:
        Union[CoingeckoFetcher, AlpacaFetcher]: The data fetcher instance.

    Raises:
        ValueError: If an unsupported category is provided.

    Example:
        fetcher = get_fetcher('crypto', 'BTC')
    """
    if category == "crypto":
        fetcher = CoingeckoFetcher(symbol=symbol)
    elif category == "stock":
        fetcher = AlpacaFetcher(symbol=symbol)
    else:
        raise ValueError(f"Unsupported category: {category}")

    return fetcher


def preprocess_data(data: pd.DataFrame, date: datetime.datetime) -> pd.DataFrame:
    """
    Preprocesses data by interpolating and filling missing values.

    Args:
        data (pd.DataFrame): The input data.
        date (datetime.datetime): The date to use as a reference.

    Returns:
        pd.DataFrame: The preprocessed data.
    """
    new_row = pd.DataFrame(
        {
            "date": [date],
            "symbol": [np.nan],
            "open": [np.nan],
            "high": [np.nan],
            "low": [np.nan],
            "close": [np.nan],
            "volume": [np.nan],
            "source": [np.nan],
            "category": [np.nan],
        }
    )
    data = pd.concat([new_row, data], ignore_index=True)
    data = data.sort_values(by="date")
    data.set_index("date", inplace=True)
    data = data.resample("1H").last()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="DataFrame.interpolate with object dtype is deprecated",
            category=FutureWarning,
        )

        # Perform the interpolation
        data = data.interpolate(method="linear")
        data.ffill(inplace=True)
        data.bfill(inplace=True)
    data.reset_index(inplace=True)
    return data


def ffill_data(symbol, category, latest_date, end_date, open, high, low, close, volume):
    full_index = pd.date_range(start=latest_date, end=end_date, freq="H")
    data = {
        "date": full_index,
        "symbol": [symbol] * len(full_index),
        "open": [open] * len(full_index),
        "high": [high] * len(full_index),
        "low": [low] * len(full_index),
        "close": [close] * len(full_index),
        "volume": [volume] * len(full_index),
        "source": ["alpaca"] * len(full_index),
        "category": [category] * len(full_index),
    }
    data["date"] = pd.to_datetime(data["date"])
    data = pd.DataFrame(data)
    data = data.sort_values(by="date")
    data.set_index("date", inplace=True)
    data = data.resample("1H").last()
    data.ffill(inplace=True)
    data.bfill(inplace=True)
    data.reset_index(inplace=True)
    data = data.drop(0)
    return data
