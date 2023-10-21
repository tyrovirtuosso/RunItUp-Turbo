"""
Database Table Creation SQL Queries

This module contains SQL queries for creating various database tables. These queries are defined as multiline
strings and can be executed to create the necessary database tables for a specific application. The tables
include 'price_data', 'metadata', 'categories', 'symbols', 'strategies', and 'trading_data'.

Each query is used to create a specific table, and the tables are related to storing and managing data for a
database-driven application.

Example usage:
    - The `create_price_data_table` query is used to create the 'price_data' table.
    - The `create_metadata_table` query is used to create the 'metadata' table.
    - Similarly, other queries are used to create their respective tables.

Note:
    - The 'IF NOT EXISTS' clause ensures that the tables are only created if they do not already exist.
    - Unique constraints and foreign keys are defined in some tables for data integrity.
"""

create_price_data_table = """
    CREATE TABLE IF NOT EXISTS price_data (
        symbol TEXT NOT NULL,
        category TEXT NOT NULL,
        source TEXT NOT NULL,
        date DATETIME NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume REAL NOT NULL,
        UNIQUE(symbol(255), category(255), source(255), date)
    )
    """

create_metadata_table = """
    CREATE TABLE IF NOT EXISTS metadata (
        symbol TEXT NOT NULL,
        category TEXT NOT NULL,
        source TEXT NOT NULL,
        earliest_date DATETIME NOT NULL,
        UNIQUE(symbol(255), category(255), source(255))
    )
    """

create_categories_table = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(255) UNIQUE
    );
    """

create_symbols_table = """
    CREATE TABLE IF NOT EXISTS symbols (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol_name VARCHAR(255),
        category_id INT,
        UNIQUE KEY symbol_category_unique (symbol_name, category_id),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );
    """

create_strategies_table = """
    CREATE TABLE IF NOT EXISTS strategies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        strategy_name VARCHAR(255) UNIQUE
    );
    """

create_trading_data_table = """
    CREATE TABLE IF NOT EXISTS trading_data (
        id INT PRIMARY KEY AUTO_INCREMENT,
        strategy_id INT,
        symbol_id INT,
        category_id INT,
        trend_type ENUM('Uptrend', 'Downtrend'),
        start_time DATETIME,
        end_time DATETIME,
        start_price REAL NOT NULL,
        end_price REAL NOT NULL,
        percentage_change DECIMAL(10, 2),
        completed BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (strategy_id) REFERENCES strategies(id),
        FOREIGN KEY (symbol_id) REFERENCES symbols(id),
        FOREIGN KEY (category_id) REFERENCES categories(id),
        UNIQUE KEY unique_trading_data (strategy_id, symbol_id, category_id, trend_type, start_time)
    );
"""

# List of all SQL queries for creating tables
mysql_create_tables = [
    create_price_data_table,
    create_metadata_table,
    create_categories_table,
    create_symbols_table,
    create_strategies_table,
    create_trading_data_table,
]
