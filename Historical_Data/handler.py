# Imports for Historical Data Handling (Crypto and Stock)
# Standard Library Imports
import datetime
import warnings
from typing import List, Union

# Third-Party Library Imports
import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

# Internal or Custom Imports
from log_config import logger

from .crypto import CoingeckoFetcher
from .stock import AlpacaFetcher

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


def ffill_data(
    db_handler, symbol: str, category: str, end_date: datetime.datetime
) -> pd.DataFrame:
    """
    Fetches and preprocesses data for a given symbol and category using forward fill.

    Args:
        db_handler: The database handler.
        symbol (str): The symbol to fetch data for.
        category (str): The category of the symbol.
        end_date (datetime.datetime): The end date for data fetching.

    Returns:
        pd.DataFrame: The fetched and preprocessed data.
    """

    # Query to get latest row
    query = """
        SELECT M.open, M.high, M.low, M.close, M.volume, M.timestamp_utc
        FROM MarketData M
        JOIN Symbols S ON M.symbol_id = S.symbol_id
        JOIN Categories C ON M.category_id = C.category_id
        WHERE S.symbol_name = 'coin' AND C.category_name = 'stock'
        AND M.timestamp_utc = (
            SELECT MAX(timestamp_utc)
            FROM MarketData
            WHERE symbol_id = S.symbol_id AND category_id = C.category_id
        );
    """
    db_handler.cursor.execute(query)
    open, high, low, close, volume, latest_date = db_handler.cursor.fetchone()
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


def insert_data(data: pd.DataFrame, db_handler) -> None:
    """
    Inserts preprocessed data into the database.

    Args:
        data (pd.DataFrame): The data to insert.
        db_handler: The database handler.
    """

    # Get or insert category and source information
    category_ids = {}
    source_ids = {}
    symbol_ids = {}
    cursor = db_handler.cursor

    logger.info("Fetching category_ids, source_ids and symbol_ids")

    for category in data["category"].unique():
        category_id = get_or_insert_category(cursor, category)
        category_ids[category] = category_id

    for source in data["source"].unique():
        source_id = get_or_insert_source(cursor, source)
        source_ids[source] = source_id

    for symbol in data["symbol"].unique():
        symbol_id = get_or_insert_symbol(cursor, symbol)
        symbol_ids[symbol] = symbol_id

    db_handler.conn.commit()
    logger.info("Fetched category_ids, source_ids and symbol_ids")

    # Create a list of tuples for batch insert
    batch_data = []

    for _, row in data.iterrows():
        category_id = category_ids.get(row["category"])
        source_id = source_ids.get(row["source"])
        symbol_id = symbol_ids.get(row["symbol"])
        batch_data.append(
            (
                row["date"],
                symbol_id,
                category_id,
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                source_id,
            )
        )

    # Define the SQL statement for batch insert
    insert_query = "INSERT INTO MarketData (timestamp_utc, symbol_id, category_id, open, high, low, close, volume, source_id) VALUES %s"

    # Use execute_values to perform batch insert
    logger.info(f"Inserting {symbol} into Database...")
    execute_values(cursor, insert_query, batch_data)
    logger.success(f"Insert for {symbol} Complete!")

    db_handler.conn.commit()


def fetch_and_insert_data(
    symbol: str,
    category: str,
    db_handler,
    start_date: Union[datetime.datetime, None] = None,
) -> None:
    """
    Fetches data for a given symbol and category and inserts it into the database.

    Args:
        symbol (str): The symbol to fetch data for.
        category (str): The category of the symbol.
        db_handler: The database handler.
        start_date (datetime.datetime, optional): The start date for data fetching. Defaults to None.
    """

    # Validate category
    validate_category(category, symbol)

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
                data = ffill_data(db_handler, symbol, category, end_date)

    if data is not None:
        insert_data(data, db_handler)
    else:
        warning_message = (
            f"\033[93mFetched Data for ({symbol}, {category}) is None.\033[0m"
        )
        logger.warning(warning_message)
        raise ValueError(warning_message)


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


def get_or_insert_category(cursor, category):
    cursor.execute(
        "SELECT category_id FROM Categories WHERE category_name = %s", (category,)
    )
    category_id = cursor.fetchone()

    if category_id is None:
        cursor.execute(
            "INSERT INTO Categories (category_name) VALUES (%s) RETURNING category_id",
            (category,),
        )
        category_id = cursor.fetchone()
    return category_id[0]


def get_or_insert_source(cursor, source):
    cursor.execute("SELECT source_id FROM Sources WHERE source_name = %s", (source,))
    source_id = cursor.fetchone()

    if source_id is None:
        cursor.execute(
            "INSERT INTO Sources (source_name) VALUES (%s) RETURNING source_id",
            (source,),
        )
        source_id = cursor.fetchone()
    return source_id[0]


def get_or_insert_symbol(cursor, symbol):
    cursor.execute("SELECT symbol_id FROM Symbols WHERE symbol_name = %s", (symbol,))
    symbol_id = cursor.fetchone()

    if symbol_id is None:
        cursor.execute(
            "INSERT INTO Symbols (symbol_name) VALUES (%s) RETURNING symbol_id",
            (symbol,),
        )
        symbol_id = cursor.fetchone()
    return symbol_id[0]
