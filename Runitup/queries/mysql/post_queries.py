from typing import List, Tuple

import pandas as pd


def insert_price_data_query(dataframe: pd.DataFrame) -> Tuple[str, List[Tuple]]:
    """
    Generate an SQL INSERT query and data tuples from a Pandas DataFrame.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing the data to be inserted.

    Returns:
        Tuple[str, List[Tuple]]: A tuple containing the SQL query and a list of data tuples.

    Example:
    query, data_tuples = insert_price_data_query(dataframe)
    cursor.execute(query, data_tuples)
    connection.commit()
    """
    table_name = "price_data"
    if not isinstance(dataframe["date"][0], str):
        dataframe["date"] = dataframe["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    columns = ", ".join(dataframe.columns)
    placeholders = ", ".join(["%s"] * len(dataframe.columns))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convert dataframe values to a list of tuples
    data_tuples = [tuple(x) for x in dataframe.values]
    return query, data_tuples


def insert_metadata_query(
    symbol: str, category: str, source: str, earliest_date: str
) -> str:
    """
    Generate an SQL INSERT query for inserting metadata into a table.

    Args:
        symbol (str): The symbol for the metadata.
        category (str): The category for the metadata.
        source (str): The source for the metadata.
        earliest_date (str): The earliest date for the metadata.

    Returns:
        str: An SQL INSERT query as a string.

    Example:
    query = insert_metadata_query('AAPL', 'Technology', 'NASDAQ', '2000-01-01')
    cursor.execute(query)
    connection.commit()
    """
    insert_query = f"INSERT INTO metadata (symbol, category, source, earliest_date) VALUES ('{symbol}', '{category}', '{source}', '{earliest_date}')"
    return insert_query
