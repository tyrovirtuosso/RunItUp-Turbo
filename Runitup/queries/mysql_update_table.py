"""
Database Table Update SQL Queries

This module contains SQL queries for updating various database tables. These queries are defined as multiline
strings and can be executed to update the database tables based on new metadata entries, to set symbol and category
IDs in the 'price_data' table, and to insert new strategies into the 'strategies' table.

Each query is used for a specific update operation related to database tables.

Example usage:
    - The `update_categories_query` is used to insert new categories into the 'categories' table based on metadata.
    - The `update_symbols_query` is used to insert new symbols into the 'symbols' table with their respective
      category IDs.
    - The `update_symbol_id_query` is used to set symbol IDs in the 'price_data' table.
    - The `update_category_id_query` is used to set category IDs in the 'price_data' table.
    - The `update_strategies_query` is used to insert new strategies into the 'strategies' table (currently commented out).

Note:
    - The 'INSERT IGNORE' is used to avoid duplicate entries.
    - The 'UPDATE' queries modify existing data in the tables.
    - Strategies can be updated using data from a 'StrategySelector', as indicated in the commented code block.
"""


update_categories_query = """
    INSERT IGNORE INTO categories (category_name)
    SELECT DISTINCT category FROM metadata
    WHERE category NOT IN (SELECT category_name FROM categories);
    """

update_symbols_query = """
    INSERT IGNORE INTO symbols (symbol_name, category_id)
    SELECT DISTINCT m.symbol, c.id
    FROM metadata m
    JOIN categories c ON m.category = c.category_name
    WHERE m.symbol NOT IN (SELECT symbol_name FROM symbols);
    """

update_symbol_id_query = """
    UPDATE price_data pd
    JOIN symbols s ON pd.symbol = s.symbol_name
    SET pd.symbol_id = s.id
    WHERE pd.symbol_id IS NULL;
"""

update_category_id_query = """
    UPDATE price_data pd
    JOIN categories c ON pd.category = c.category_name
    SET pd.category_id = c.id
    WHERE pd.category_id IS NULL;
"""

update_strategies_query = """
    INSERT IGNORE INTO strategies (strategy_name)
    VALUES (%s)
    """

# strategy_selector = StrategySelector()
# strategies = strategy_selector.view_strategies()
# for strategy_name, description in strategies:
#     self.cursor.execute(update_strategies_query, (strategy_name,))


# List of all SQL queries for updating tables
mysql_update_tables = [
    update_categories_query,
    update_symbols_query,
    update_symbol_id_query,
    update_category_id_query,
]
