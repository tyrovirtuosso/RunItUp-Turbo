def get_unique_symbols() -> str:
    """
    Retrieve a list of unique symbols and their latest date from the price_data table.

    Returns:
    str: SQL query to select unique symbols and their latest dates.
    """
    return """
    SELECT symbol, category, MAX(date) as latest_date
    FROM price_data
    GROUP BY symbol, category;
    """


def get_metadata_of_symbol(symbol: str, category: str, source: str) -> str:
    """
    Retrieve metadata for a specific symbol, category, and source.

    Args:
    symbol (str): The symbol of the asset.
    category (str): The category of the asset.
    source (str): The source of the metadata.

    Returns:
    str: SQL query to select metadata for the specified symbol, category, and source.
    """
    query = f"SELECT * FROM metadata WHERE symbol = '{symbol}' AND category = '{category}' AND source = '{source}'"
    return query
