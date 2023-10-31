# Standard Library Imports
from typing import List, Tuple

# Third-Party Library Imports
from sqlalchemy import and_, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from log_config import logger
from Runitup.constants import DB_ENGINE

# Local Imports
from .models import Category, MarketData, Source, Symbol

engine = DB_ENGINE


def get_unique_symbol_category_pairs() -> List[Tuple[str, str]]:
    """
    Retrieve unique symbol-category pairs from the database.

    Returns:
        List[Tuple[str, str]]: List of unique symbol-category pairs.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            query = (
                select(Symbol.symbol_name, Category.category_name)
                .distinct()
                .join(MarketData, MarketData.symbol_id == Symbol.symbol_id)
                .join(Category, MarketData.category_id == Category.category_id)
            )

            results = session.execute(query)
            unique_pairs = [
                (result.symbol_name, result.category_name) for result in results
            ]
            return unique_pairs
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_latest_market_data(symbol_name: str, category_name: str):
    """
    Get the latest market data for a given symbol and category.

    Args:
        symbol_name (str): The symbol name.
        category_name (str): The category name.

    Returns:
        Tuple: A tuple containing market data (open, high, low, close, volume, timestamp_utc).
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            # Define the subquery to get the maximum timestamp
            subquery = (
                session.query(
                    MarketData.symbol_id,
                    MarketData.category_id,
                    func.max(MarketData.timestamp_utc).label("max_timestamp"),
                )
                .group_by(MarketData.symbol_id, MarketData.category_id)
                .subquery()
            )

            # Perform the join operations
            query = (
                session.query(
                    MarketData.open,
                    MarketData.high,
                    MarketData.low,
                    MarketData.close,
                    MarketData.volume,
                    MarketData.timestamp_utc,
                )
                .join(Symbol, MarketData.symbol_id == Symbol.symbol_id)
                .join(Category, MarketData.category_id == Category.category_id)
                .join(
                    subquery,
                    and_(
                        MarketData.symbol_id == subquery.c.symbol_id,
                        MarketData.category_id == subquery.c.category_id,
                        MarketData.timestamp_utc == subquery.c.max_timestamp,
                    ),
                )
                .filter(
                    and_(
                        Symbol.symbol_name == symbol_name,
                        Category.category_name == category_name,
                    )
                )
            )
            results = query.all()
            for row in results:
                return row
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_or_insert_category(category_name: str) -> int:
    """
    Get or insert a category in the database.

    Args:
        category_name (str): The name of the category.

    Returns:
        int: The category ID.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            # Try to find the category by name
            existing_category = (
                session.query(Category)
                .filter(Category.category_name == category_name)
                .first()
            )

            if existing_category is None:
                # Category doesn't exist, create a new one
                new_category = Category(category_name=category_name)
                session.add(new_category)
                session.commit()
                return new_category.category_id
            else:
                return existing_category.category_id
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_or_insert_source(source_name: str) -> int:
    """
    Get or insert a source in the database.

    Args:
        source_name (str): The name of the source.

    Returns:
        int: The source ID.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            # Try to find the source by name
            existing_source = (
                session.query(Source).filter(Source.source_name == source_name).first()
            )

            if existing_source is None:
                # Source doesn't exist, create a new one
                new_source = Source(source_name=source_name)
                session.add(new_source)
                session.commit()
                return new_source.source_id
            else:
                return existing_source.source_id
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_or_insert_symbol(symbol_name: str) -> int:
    """
    Get or insert a symbol in the database.

    Args:
        symbol_name (str): The name of the symbol.

    Returns:
        int: The symbol ID.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            # Try to find the symbol by name
            existing_symbol = (
                session.query(Symbol).filter(Symbol.symbol_name == symbol_name).first()
            )

            if existing_symbol is None:
                # Symbol doesn't exist, create a new one
                new_symbol = Symbol(symbol_name=symbol_name)
                session.add(new_symbol)
                session.commit()
                return new_symbol.symbol_id
            else:
                return existing_symbol.symbol_id
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def batch_insert_market_data(data: List[dict], batch_size: int = 100000):
    """
    Batch insert market data into the database.

    Args:
        data (List[dict]): List of dictionaries containing market data.
        batch_size (int): The size of each batch for insertion.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            # Split data into batches
            batches = [
                data[i : i + batch_size] for i in range(0, len(data), batch_size)
            ]

            # Use bulk_insert_mappings to perform batch insert for each batch
            i = 0
            batches_len = len(batches)

            for batch in batches:
                i += 1
                session.bulk_insert_mappings(MarketData, batch)
                logger.info(f"Inserting: {i}/{batches_len}")
            session.commit()
            break
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()


def get_unique_symbols_and_categories_with_latest_date() -> List[Tuple[str, str, str]]:
    """
    Retrieve unique symbols and categories with their latest date from the database.

    Returns:
        List[Tuple[str, str, str]]: List of unique symbol, category, and latest date tuples.
    """
    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            query = (
                session.query(
                    Symbol.symbol_name,
                    Category.category_name,
                    func.max(MarketData.timestamp_utc).label("latest_date"),
                )
                .join(Symbol, MarketData.symbol_id == Symbol.symbol_id)
                .join(Category, MarketData.category_id == Category.category_id)
                .group_by(Symbol.symbol_name, Category.category_name)
            )
            results = query.all()
            return results
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_row_count():
    """
    Get the row count in the MarketData table.

    Args:
        session (Session): SQLAlchemy database session.
        MarketData (class): SQLAlchemy model class for MarketData.

    Returns:
        int: The total row count, or -1 in case of failure.
    """

    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            total_row_count = session.query(MarketData).count()
            return total_row_count
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")


def get_symbol_count():
    """
    Get the symbol count in the Symbol table.

    Args:
        session (Session): SQLAlchemy database session.
        Symbol (class): SQLAlchemy model class for Symbol.

    Returns:
        int: The total symbol count, or -1 in case of failure.
    """

    Session = sessionmaker(bind=engine)
    max_retries = 5
    for i in range(max_retries):
        session = Session()
        try:
            total_symbol_count = session.query(Symbol).count()
            return total_symbol_count
        except OperationalError as e:
            logger.error(
                f"Error executing query: {e}. Retrying... ({i+1}/{max_retries})"
            )
            session.rollback()
        finally:
            session.close()
    logger.error(f"Failed to execute query after {max_retries} attempts.")
