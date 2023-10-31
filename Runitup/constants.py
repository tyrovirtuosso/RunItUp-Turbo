# Standard Library Imports
import json
import os
import urllib
from typing import Dict, List, Tuple, Union

# Third-Party Library Imports
import yaml
from sqlalchemy import create_engine

# Internal or Custom Imports
from Runitup.symbols import BUCKET

config_path = "Runitup/configs/runitup_config.yaml"
config_path = os.path.abspath(config_path)


def load_config(
    config_file_path: str,
) -> Dict[str, Union[bool, Dict[str, Union[str, int]]]]:
    """
    Load the configuration from a YAML file.

    Args:
        config_file_path (str): Path to the configuration YAML file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    with open(config_file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


def get_db_engine():
    config = load_config(config_path)
    if config["system"]["development"]:
        db_config = config["db"]
    else:
        db_config = config["prod_db"]

    # Map the database type to the SQLAlchemy driver
    db_type = db_config["type"].lower()

    if db_type == "azure_db":
        params = urllib.parse.quote_plus(
            f"DRIVER={{{db_config['driver']}}};SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};UID={db_config['username']};PWD={db_config['password']}"
        )
        db_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        return db_engine

    elif db_type == "local-postgre":
        conn_str = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        db_engine = create_engine(conn_str)
        return db_engine

    elif db_type == "neon-postgre":
        conn_str = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['database']}?sslmode=require"
        db_engine = create_engine(conn_str)
        return db_engine
    else:
        raise ValueError("Unsupported database type")


def collect_unique_symbol_category_pairs(
    bucket_data: List[Dict[str, Union[str, List[Dict[str, str]]]]]
) -> List[Tuple[str, str]]:
    """
    Collect unique symbol-category pairs from the provided bucket data.

    Args:
        bucket_data (List[Dict[str, Union[str, List[Dict[str, str]]]]): List of bucket data.

    Returns:
        List[Tuple[str, str]]: List of unique symbol-category pairs.
    """
    unique_symbol_category_pairs = set()

    for bucket in bucket_data:
        for symbol, symbol_info in bucket["symbols"].items():
            unique_symbol_category_pairs.add((symbol, symbol_info["category"]))

    return list(unique_symbol_category_pairs)


def get_current_folder_path() -> str:
    """
    Get the path to the current folder and create a JSON file if it doesn't exist.

    Returns:
        str: The path to the JSON file for storing Telegram notifications.
    """

    current_file_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_file_path)
    TELEGRAM_NOTIFICATION_FILE_PATH = os.path.join(
        directory_path, "telegram_notifications.json"
    )

    if not os.path.exists(TELEGRAM_NOTIFICATION_FILE_PATH):
        # Create an empty dictionary
        notifications = {}

        # Save the empty dictionary to create the file
        with open(TELEGRAM_NOTIFICATION_FILE_PATH, "w") as file:
            json.dump(notifications, file, indent=4)

    return TELEGRAM_NOTIFICATION_FILE_PATH


TELEGRAM_NOTIFICATION_FILE_PATH = get_current_folder_path()
LOCAL_SYMBOLS: List[Tuple[str, str]] = collect_unique_symbol_category_pairs(BUCKET)
DB_ENGINE = get_db_engine()
