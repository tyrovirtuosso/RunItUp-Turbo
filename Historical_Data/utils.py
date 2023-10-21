# noqa
"""
This module provides utility functions for Historical Data Fetching

Imports:
- os: Module for interacting with the operating system.
- datetime from datetime: Module for manipulating dates and times.
- List, Optional from typing: Type hints for lists and optional values.
- pandas as pd: Library for data manipulation and analysis.
- logger from Historical_Data.log_config: Custom logger for logging messages.

Function: export_to_csv
- Method to export the data to a CSV file.
- Parameters:
    - df: Data to export as a DataFrame.
    - file_name: Name of the CSV file to be created (default is 'data').
    - cols_to_remove: Optional list of column names to remove before exporting.
- Returns: None

Function: get_earliest_common_date
- Get the earliest common date among a dictionary of DataFrames.
- Parameters:
    - dataframes: Dictionary of DataFrames with a 'date' column.
- Returns: The earliest common date as a datetime object.

Function: slice_from_earliest_common_date
- Slice the DataFrames from the earliest common date or a specified date.
- Parameters:
    - dataframes: Dictionary of DataFrames with a 'date' column.
    - earliest_date: Optional earliest date to slice from, if not provided, it's calculated.
- Returns: A dictionary of sliced DataFrames.

Please note that the code relies on the pandas library for data manipulation and the log_config module for logging.
"""


# System and Standard Library Imports
import os
from datetime import datetime
from typing import List, Optional

# Third-Party Library Imports
import pandas as pd

# Local Imports
from log_config import logger


def export_to_csv(
    df: pd.DataFrame,
    file_name: str = "data",
    cols_to_remove: Optional[List[str]] = None,
) -> None:
    """
    Method to export the data to a CSV file.

    param df: Data to export as a DataFrame.
    param file_name: Name of the CSV file to be created (default is 'data').
    param cols_to_remove: Optional list of column names to remove before exporting.

    :return: None
    """
    df = df.copy()

    if cols_to_remove and not isinstance(cols_to_remove, list):
        cols_to_remove = [cols_to_remove]

    # Get the current directory of the script
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Create a 'data' directory if it doesn't exist
    data_dir = os.path.join(current_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Construct the file path for the CSV file
    file_path = os.path.join(data_dir, f"{file_name}.csv")

    if df.empty:
        print("Dataframe to export is empty")
        logger.error("Dataframe to export is empty")
        return None

    if cols_to_remove:
        df.drop(cols_to_remove, axis=1, level=1, inplace=True)

    # Export the DataFrame to a CSV file with an index
    df.to_csv(file_path, index=True)


def get_earliest_common_date(dataframes: dict) -> datetime:
    """
    Get the earliest common date among a dictionary of DataFrames.

    :param dataframes: Dictionary of DataFrames with a 'date' column.

    :return: The earliest common date as a datetime object.
    """
    earliest_common_date = None

    for df in dataframes.values():
        df["date"] = pd.to_datetime(df["date"])
        current_date = df["date"].iloc[0]

        if earliest_common_date is None or current_date > earliest_common_date:
            earliest_common_date = current_date

    return earliest_common_date


def slice_from_earliest_common_date(
    dataframes: dict, earliest_date: Optional[datetime] = None
) -> dict:
    """
    Slice the DataFrames from the earliest common date or a specified date.

    :param dataframes: Dictionary of DataFrames with a 'date' column.
    :param earliest_date: Optional earliest date to slice from, if not provided, it's calculated.

    :return: A dictionary of sliced DataFrames.
    """
    if earliest_date is None:
        earliest_date = get_earliest_common_date(dataframes)

    for symbol, df in dataframes.items():
        sliced_df = df[df["date"] >= earliest_date].reset_index(drop=True)
        dataframes[symbol] = sliced_df

    return dataframes
