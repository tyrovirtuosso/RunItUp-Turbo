# Logging Configuration
# Type Hints
from typing import List, Set, Tuple

from log_config import logger

# Configuration and Constants
from .constants import DEVELOPMENT_MODE, LOCAL_SYMBOLS

# Database Operations
from .db_operations import fetch_and_insert_data, get_missing_pairs, initialize_db

# Database Query Imports
from .queries.mysql.get_queries import get_unique_symbols


def fetch_missing_data():
    """
    Fetch missing data for symbols in LOCAL_SYMBOLS and insert it into the database.
    """
    if DEVELOPMENT_MODE:
        db_handler = initialize_db()

        # Get unique symbols from the database
        db_symbols: List[Tuple[str, str, str]] = db_handler.execute_get_query(
            get_unique_symbols()
        )

        # Find missing symbol-category pairs
        missing_pairs: Set[Tuple[str, str]] = get_missing_pairs(
            db_symbols, LOCAL_SYMBOLS
        )

        if missing_pairs:
            logger.info(f"Fetching missing symbols: {missing_pairs}")
            for item in missing_pairs:
                symbol, category = item
                try:
                    fetch_and_insert_data(symbol, category, db_handler)
                except Exception as e:
                    print(e)
                    logger.error(e)


# Call the fetch_missing_data function to trigger the data fetching process
if __name__ == "__main__":
    fetch_missing_data()
