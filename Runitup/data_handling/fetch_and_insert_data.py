# Standard Library Imports
import datetime
from typing import Union

# Third-Party Library Imports
import pandas as pd

# Custom Logger Import
from log_config import logger
from Runitup.db_models import (
    batch_insert_market_data,
    get_latest_market_data,
    get_or_insert_category,
    get_or_insert_source,
    get_or_insert_symbol,
)

# Custom Imports
from .utils import ffill_data, get_fetcher, preprocess_data, validate_category


def insert_data(data: pd.DataFrame) -> None:
    """
    Inserts preprocessed data into the database.

    Args:
        data (pd.DataFrame): The data to insert.
    """
    # Get or insert category and source information
    category_ids = {}
    source_ids = {}
    symbol_ids = {}

    logger.info("Fetching category_ids, source_ids and symbol_ids")

    for category in data["category"].unique():
        category_id = get_or_insert_category(category)
        category_ids[category] = category_id

    for source in data["source"].unique():
        source_id = get_or_insert_source(source)
        source_ids[source] = source_id

    for symbol in data["symbol"].unique():
        symbol_id = get_or_insert_symbol(symbol)
        symbol_ids[symbol] = symbol_id

    logger.info("Fetched category_ids, source_ids and symbol_ids")
    logger.info(f"Inserting {symbol} into Database...")

    # Create a list of tuples for batch insert
    batch_data = []

    for _, row in data.iterrows():
        category_id = category_ids.get(row["category"])
        source_id = source_ids.get(row["source"])
        symbol_id = symbol_ids.get(row["symbol"])
        timestamp_utc = row["date"]

        row_dict = {
            "timestamp_utc": timestamp_utc,
            "symbol_id": symbol_id,
            "category_id": category_id,
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
            "source_id": source_id,
        }
        batch_data.append(row_dict)

    batch_insert_market_data(batch_data)
    logger.success(f"Insert for {symbol} Complete!")


def fetch_data(
    symbol: str,
    category: str,
    start_date: Union[datetime.datetime, None] = None,
) -> pd.DataFrame:
    """
    Fetches data for a given symbol.

    Args:
        symbol (str): The symbol to fetch data for.
        category (str): The category of the symbol.
        start_date (datetime.datetime, optional): The start date for data fetching. Defaults to None.

    Returns:
        pd.DataFrame: The fetched data.
    """
    # Fetch data using the appropriate fetcher
    fetcher = get_fetcher(category.lower(), symbol)

    # Fetch from beginning if no start date is given
    if not start_date:
        data = fetcher.fetch_raw_data(start_date=fetcher.get_earliest_price())
    else:
        # Fetch from start date
        if category.lower() == "crypto":
            data = fetcher.fetch_raw_data(start_date=start_date)

        # Preprocessing is required as stock data is not 24/7 and has holidays
        elif category.lower() == "stock":
            current_utc_datetime = datetime.datetime.utcnow()
            current_utc_datetime = current_utc_datetime.replace(
                minute=0, second=0, microsecond=0
            )
            end_date = current_utc_datetime - datetime.timedelta(hours=1)
            data = fetcher.fetch_raw_data(start_date=start_date)

            if not data.empty:
                # Check if fetched data actually starts from start date
                if data["date"][0] != start_date:
                    data = preprocess_data(start_date)

                    # Check if fetched data actually ends on end date
                    last_date = (
                        data["date"].tail(1).dt.strftime("%Y-%m-%d %H:%M:%S").values[0]
                    )
                    last_date = pd.to_datetime(last_date)
                    if last_date < end_date:
                        data = preprocess_data(end_date)

            else:
                # If data is empty, it means its a holiday. In that case ffill the values
                open, high, low, close, volume, latest_date = get_latest_market_data(
                    symbol, category
                )
                data = ffill_data(
                    symbol,
                    category,
                    latest_date,
                    end_date,
                    open,
                    high,
                    low,
                    close,
                    volume,
                )
    return data


def fetch_and_insert_data(
    symbol: str,
    category: str,
    start_date: Union[datetime.datetime, None] = None,
) -> None:
    """
    Fetches and inserts data for a given symbol.

    Args:
        symbol (str): The symbol to fetch data for.
        category (str): The category of the symbol.
        start_date (datetime.datetime, optional): The start date for data fetching. Defaults to None.
    """

    # Validate Category
    validate_category(category, symbol)

    # Fetch Data
    data = fetch_data(symbol, category, start_date)

    if data is not None:
        # Insert Data
        insert_data(data)
    else:
        warning_message = (
            f"\033[93mFetched Data for ({symbol}, {category}) is None.\033[0m"
        )
        logger.warning(warning_message)
        raise ValueError(warning_message)
