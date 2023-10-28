# Standard Library Imports
import datetime
import time

# Third-Party Library Imports
from pandas import Timestamp, to_datetime

from Historical_Data.handler import fetch_and_insert_data
from log_config import logger
from Storage.handler import initialize_db

# Internal or Custom Imports
from .constants import DB_PARAMS, LOCAL_SYMBOLS
from .queries import (
    create_table_script,
    get_latest_date_script,
    get_symbol_category_script,
)


def fetch_missing_data(db_handler) -> None:
    """
    Fetch missing data for symbols in LOCAL_SYMBOLS and insert it into the database.

    Args:
        db_handler: Database handler for executing queries.
    """
    db_handler.execute_scripts(create_table_script, query_type="post")
    db_symbols = db_handler.execute_scripts(
        get_symbol_category_script, query_type="get"
    )
    db_symbols_set = set((symbol, category) for symbol, category in db_symbols)
    LOCAL_SYMBOLS_set = set(LOCAL_SYMBOLS)
    missing_pairs = LOCAL_SYMBOLS_set - db_symbols_set

    if missing_pairs:
        logger.info(f"Fetching missing symbols: {missing_pairs}")
        for item in missing_pairs:
            symbol, category = item
            try:
                fetch_and_insert_data(symbol, category, db_handler)
            except Exception as e:
                logger.error(e)


def update_data(db_handler) -> None:
    """
    Update data for symbols in the database based on the latest date.

    Args:
        db_handler: Database handler for executing queries.
    """
    latest_symbols = db_handler.execute_scripts(
        get_latest_date_script, query_type="get"
    )
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
                fetch_and_insert_data(
                    symbol, category, db_handler, start_date=start_date
                )
            except Exception as e:
                logger.error(e)

        completed_items += 1
        progress = int(completed_items / total_items * max_bar_length)
        bar = "[" + "#" * progress + " " * (max_bar_length - progress) + "]"
        print(f"\r{bar} {completed_items}/{total_items} - {item[0]} data", end="")
        time.sleep(0.1)


if __name__ == "__main__":
    db_handler = initialize_db(DB_PARAMS)
    fetch_missing_data(db_handler)
    update_data(db_handler)
