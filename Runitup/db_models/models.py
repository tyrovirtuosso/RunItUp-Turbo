# Third-party Library Imports
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base

# Local Imports
from log_config import logger
from Runitup.constants import DB_ENGINE

# Create a base class for declarative models
Base = declarative_base()


class Category(Base):
    """
    Define the Categories table.

    Attributes:
        category_id (int): The unique identifier for the category.
        category_name (str): The name of the category (up to 20 characters).
    """

    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(20), nullable=False)


class Source(Base):
    """
    Define the Sources table.

    Attributes:
        source_id (int): The unique identifier for the source.
        source_name (str): The name of the source (up to 20 characters).
    """

    __tablename__ = "sources"

    source_id = Column(Integer, primary_key=True)
    source_name = Column(String(20), nullable=False)


class Symbol(Base):
    """
    Define the Symbols table.

    Attributes:
        symbol_id (int): The unique identifier for the symbol.
        symbol_name (str): The name of the symbol (up to 30 characters).
    """

    __tablename__ = "symbols"

    symbol_id = Column(Integer, primary_key=True)
    symbol_name = Column(String(50), nullable=False)


class MarketData(Base):
    """
    Define the MarketData table.

    Attributes:
        market_data_id (int): The unique identifier for market data.
        timestamp_utc (TIMESTAMP): The timestamp of the data (not nullable).
        category_id (int): The foreign key reference to categories (not nullable).
        symbol_id (int): The foreign key reference to symbols (not nullable).
        open (Numeric): The opening price (not nullable).
        high (Numeric): The highest price (not nullable).
        low (Numeric): The lowest price (not nullable).
        close (Numeric): The closing price (not nullable).
        volume (Numeric): The trading volume (not nullable).
        source_id (int): The foreign key reference to sources (not nullable).
    """

    __tablename__ = "marketdata"

    market_data_id = Column(Integer, primary_key=True)
    timestamp_utc = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"), nullable=False)
    open = Column(Numeric(precision=12, scale=2), nullable=False)
    high = Column(Numeric(precision=12, scale=2), nullable=False)
    low = Column(Numeric(precision=12, scale=2), nullable=False)
    close = Column(Numeric(precision=12, scale=2), nullable=False)
    volume = Column(Numeric(precision=20, scale=8), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.source_id"), nullable=False)

    # Define a unique constraint
    __table_args__ = (UniqueConstraint("timestamp_utc", "category_id", "symbol_id"),)


def create_models():
    """
    Create database models if they don't exist.

    Args:
        engine: The SQLAlchemy engine to use for model creation.

    Returns:
        None
    """
    try:
        Base.metadata.create_all(DB_ENGINE)
    except OperationalError as e:
        logger.error(f"Error creating database models: {e}")
