import pandas as pd

from Historical_Data.log_config import logger


def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validates the structure and data types of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to be validated.

    Returns:
    bool: True if the DataFrame is valid, False otherwise.
    """
    expected_dtypes = {
        "date": "datetime64[ns]",
        "close": float,
        "open": float,
        "high": float,
        "low": float,
        "volume": float,
        "symbol": object,
        "source": object,
        "category": object,
    }

    for column, expected_dtype in expected_dtypes.items():
        if df[column].dtype != expected_dtype:
            logger.error(
                f"Invalid dtype for column '{column}'. Expected: {expected_dtype}, Actual: {df[column].dtype}"
            )
            return False

    logger.success("Dataframe is validated successfully!")
    return True
