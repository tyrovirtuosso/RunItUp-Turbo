# Standard Library Imports
import datetime
import time

# Third-Party Library Imports
from pandas import Timestamp, to_datetime

# Internal or Custom Imports
from log_config import logger

from .constants import LOCAL_SYMBOLS
from .data_handling import fetch_and_insert_data
from .db_models import (
    create_models,
    get_unique_symbol_category_pairs,
    get_unique_symbols_and_categories_with_latest_date,
)


def fetch_missing_data() -> None:
    """
    Fetch missing data for local symbols and insert it into the database.

    This function fetches data for local symbols that are not already in the database and inserts it into the database.

    Returns:
        None
    """
    # Create Models if not exists
    create_models()

    # Get Unique symbol, category pairs
    db_symbols = get_unique_symbol_category_pairs()
    logger.info("Unique symbol category pairs fetched")

    db_symbols_set = set((symbol, category) for symbol, category in db_symbols)
    LOCAL_SYMBOLS_set = set(LOCAL_SYMBOLS)
    missing_pairs = LOCAL_SYMBOLS_set - db_symbols_set

    print(f"Missing Symbols from DB: {missing_pairs}")
    if missing_pairs:
        logger.info(f"Fetching missing symbols: {missing_pairs}")
        for item in missing_pairs:
            symbol, category = item
            try:
                fetch_and_insert_data(symbol, category)
            except Exception as e:
                logger.error(e)


def update_data() -> None:
    """
    Update data for unique symbols and categories with the latest date.

    This function updates data for unique symbols and categories with the latest date. It iterates through the symbols and updates their data if necessary.

    Returns:
        None
    """
    latest_symbols = get_unique_symbols_and_categories_with_latest_date()
    total_items = len(latest_symbols)
    completed_items = 0
    max_bar_length = 50
    ONE_HOUR = 3600

    for item in latest_symbols:
        symbol, category, latest_date = item
        start_date = to_datetime(latest_date) + datetime.timedelta(hours=1)
        end_date = (
            (
                to_datetime(Timestamp.utcnow()).replace(tzinfo=None)
                - datetime.timedelta(minutes=16)
            )
            if category == "stock"
            else (to_datetime(Timestamp.utcnow()).replace(tzinfo=None)).replace(
                minute=0, second=0, microsecond=0
            )
        )

        if (
            start_date < end_date
            and (end_date - start_date).total_seconds() >= ONE_HOUR
        ):
            try:
                logger.info(f"Updating {symbol}")
                fetch_and_insert_data(symbol, category, start_date=start_date)
            except Exception as e:
                logger.exception(e)

        completed_items += 1
        progress = int(completed_items / total_items * max_bar_length)
        bar = "[" + "#" * progress + " " * (max_bar_length - progress) + "]"
        print(f"\r{bar} {completed_items}/{total_items} - {item[0]} data", end="")
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        fetch_missing_data()
        update_data()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
