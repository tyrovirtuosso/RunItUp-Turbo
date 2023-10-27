# Imports related to Typing
from typing import List, Set, Tuple, Union

# Imports for Database Handling
from DB_Handler.rdb.mysql_handler import MySQL
from DB_Handler.rdb.postgre_handler import Postgre

# Imports for Historical Data Handling (Crypto and Stock)
from Historical_Data.crypto import CoingeckoFetcher
from Historical_Data.stock import AlpacaFetcher

# Logging Configuration
from log_config import logger

# Imports related to Constants and Database Parameters
from .constants import DB_PARAMS

# Imports for MySQL Queries
from .queries.mysql import mysql_create_tables, mysql_update_tables
from .queries.mysql.get_queries import get_metadata_of_symbol
from .queries.mysql.post_queries import insert_metadata_query, insert_price_data_query


def initialize_db() -> Union[MySQL, None]:
    """
    Initialize the database handler based on DB_PARAMS configuration.

    Returns:
        MySQL or None: An instance of the MySQL database handler or None if the type is not supported.
    """
    if DB_PARAMS["type"].lower() == "mysql":
        db_handler = MySQL(DB_PARAMS)
        db_handler.create_tables(mysql_create_tables)
        db_handler.update_tables(mysql_update_tables)
        return db_handler

    elif DB_PARAMS["type"].lower() == "postgre":
        db_handler = Postgre(DB_PARAMS)

        with open("Runitup/queries/postgre/create_table.sql", "r") as file:
            create_table_script = file.read()
        db_handler.execute_scripts(create_table_script)
        return db_handler

    return None


def get_missing_pairs(
    db_symbols: List[Tuple[str, str, str]], LOCAL_SYMBOLS: List[Tuple[str, str]]
) -> Set[Tuple[str, str]]:
    """
    Find the missing pairs between database symbols and local symbols.

    Args:
        db_symbols (List[Tuple[str, str, str]): List of symbols, categories, and sources from the database.
        LOCAL_SYMBOLS (List[Tuple[str, str]): List of local symbols and categories.

    Returns:
        Set[Tuple[str, str]]: A set of missing symbol-category pairs.
    """
    db_symbols_set = set([(symbol, category) for symbol, category, _ in db_symbols])
    LOCAL_SYMBOLS_set = set(LOCAL_SYMBOLS)
    missing_pairs = LOCAL_SYMBOLS_set - db_symbols_set
    return missing_pairs


def fetch_and_insert_data(symbol: str, category: str, db_handler: MySQL) -> None:
    """
    Fetch data and insert it into the database.

    Args:
        symbol (str): The symbol to fetch data for.
        category (str): The category of the symbol (e.g., 'crypto' or 'stock').
        db_handler (MySQL): The database handler to use for data insertion.

    Raises:
        ValueError: If an unsupported symbol-category is provided or if fetched data is None.
    """
    if category.lower() == "crypto":
        fetcher = CoingeckoFetcher(symbol=symbol)
    elif category.lower() == "stock":
        fetcher = AlpacaFetcher(symbol=symbol)
    else:
        error_message = (
            f"\033[93mUnsupported symbol-category: ({symbol}, {category})\033[0m"
        )
        logger.error(error_message)
        raise ValueError(error_message)

    data = fetcher.fetch_raw_data(start_date=fetcher.get_earliest_price())

    if data is not None:
        insert_query, data_tuples = insert_price_data_query(data)
        db_handler.execute_post_query(insert_query, data_tuples)

        get_metadata_query = get_metadata_of_symbol(
            data["symbol"][0], data["category"][0], data["source"][0]
        )
        result = db_handler.execute_get_query(get_metadata_query)

        if result is None or len(result) == 0:
            insert_query = insert_metadata_query(
                data["symbol"][0],
                data["category"][0],
                data["source"][0],
                str(data["date"][0]),
            )
            db_handler.execute_post_query(insert_query)
    else:
        warning_message = (
            f"\033[93mFetched Data for ({symbol}, {category}) is None.\033[0m"
        )
        logger.warning(warning_message)
        raise ValueError(warning_message)
