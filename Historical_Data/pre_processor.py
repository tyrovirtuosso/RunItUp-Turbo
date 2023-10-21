# Standard library imports
import datetime
import warnings

# Third-party library imports
import pandas as pd

# Custom module imports
from Historical_Data.utils import export_to_csv
from log_config import logger


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the input DataFrame by preprocessing and exporting it to CSV.

    Args:
        df (pd.DataFrame): Input DataFrame with historical data.

    Returns:
        pd.DataFrame: Cleaned and processed DataFrame.
    """
    df = preprocess_data(df)
    symbol = df["symbol"][0]
    logger.success(f"Finished cleaning {symbol}!")

    export_to_csv(df, symbol)
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the input DataFrame by applying a series of data cleaning steps.

    Args:
        df (pd.DataFrame): Input DataFrame with historical data.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    df = convert_columns_to_lowercase(df)
    df = convert_strings_to_lowercase(df)
    df = enforce_data_type(df)
    df = reset_index_if_needed(df)
    df = rename_timestamp_to_date(df)
    df = convert_date_column_to_datetime(df)
    df = remove_timezone_from_date(df)
    df = set_date_as_index(df)
    df = resample_to_1_hour_intervals(df)
    df = remove_incomplete_data(df)
    df = interpolate_and_impute_missing_data(df)
    df = reset_index_to_date(df)
    return df


def convert_columns_to_lowercase(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts all column names and string values in the DataFrame to lowercase.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with lowercase column names and values.
    """
    df.columns = [col.lower() for col in df.columns]
    df = df.apply(lambda x: x.lower() if isinstance(x, str) else x)
    return df


def convert_strings_to_lowercase(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all string values in the DataFrame to lowercase.

    Args:
        df (DataFrame): The DataFrame to process.

    Returns:
        DataFrame: The DataFrame with string values converted to lowercase.

    Example usage:
    ```
    df = convert_strings_to_lowercase(df)
    ```
    """
    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)
    return df


def enforce_data_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce data types for specific columns in the DataFrame.

    Args:
        df (DataFrame): The DataFrame to process.

    Returns:
        DataFrame: The DataFrame with enforced data types.

    Example usage:
    ```
    df = enforce_data_type(df)
    ```

    This function enforces data types for the following columns:
    - "symbol", "source", and "category" are converted to strings.
    - "open", "high", "low", "close", and "volume" are converted to floating-point numbers.
    """
    df["symbol"] = df["symbol"].astype(str)
    string_list = ["symbol", "source", "category"]
    float_list = ["open", "high", "low", "close", "volume"]
    df[string_list] = df[string_list].astype(str)
    df[float_list] = df[float_list].apply(pd.to_numeric, errors="coerce")
    return df


def reset_index_if_needed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resets the index of the DataFrame to a RangeIndex if it's not already.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with a reset index if needed.
    """
    if not df.index.equals(pd.RangeIndex(start=0, stop=len(df))):
        df = df.reset_index()
    return df


def rename_timestamp_to_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames the 'timestamp' column to 'date' if it exists in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the 'timestamp' column renamed to 'date' if present.
    """
    if "timestamp" in df.columns:
        df.rename(columns={"timestamp": "date"}, inplace=True)
    return df


def convert_date_column_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the 'date' column to a datetime format.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the 'date' column converted to datetime.
    """
    try:
        df["date"] = pd.to_datetime(
            df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
    except ValueError as e:
        logger.error(f"Error converting date column: {e}")
    return df


def remove_timezone_from_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes timezone information from the 'date' column.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with timezone information removed from the 'date' column.
    """
    df["date"] = df["date"].dt.tz_localize(None)
    return df


def set_date_as_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sets the 'date' column as the index of the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with 'date' column as the index.
    """
    df.set_index("date", inplace=True)
    return df


def resample_to_1_hour_intervals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resamples the DataFrame to 1-hour intervals, taking the last value within each hour.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Resampled DataFrame.
    """
    df = df.resample("1H").last()
    return df


def remove_incomplete_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes the last row from the DataFrame if its date is the same as the current UTC time.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the last row removed if its date matches the current UTC time.
    """
    latest_index = df.index[-1]
    latest_utc_datetime = latest_index.strftime("%Y %m %d %H")
    current_utc_datetime = datetime.datetime.utcnow().strftime("%Y %m %d %H")
    if latest_utc_datetime == current_utc_datetime:
        df = df.drop(df.index[-1])
    return df


def check_for_missing_dates(df: pd.DataFrame) -> int:
    """
    Checks for missing dates in the DataFrame and returns the count of missing dates.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        int: Count of missing dates in the DataFrame.
    """
    start_date = df.index.min()
    end_date = df.index.max()
    full_index = pd.date_range(start=start_date, end=end_date, freq="H")
    missing_dates = full_index.difference(df.index)
    return len(missing_dates)


def interpolate_and_impute_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolates and imputes missing data in the DataFrame using linear interpolation.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing data imputed using linear interpolation.
    """

    # Filter out the specific warning
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="DataFrame.interpolate with object dtype is deprecated",
            category=FutureWarning,
        )

        # Perform the interpolation
        df = df.interpolate(method="linear")
        df.ffill(inplace=True)

    return df


def reset_index_to_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resets the index of the DataFrame and renames the index column to 'date'.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the index reset and renamed.
    """
    df.reset_index(inplace=True)
    df.rename(columns={"index": "date"}, inplace=True)
    return df
