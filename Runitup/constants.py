# External libraries
# Type hinting
from typing import Dict, List, Tuple, Union

import yaml

# Custom or project-specific modules
from Runitup.symbols import BUCKET


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


config_path = "Runitup/runitup_config.yaml"
config = load_config(config_path)

DEVELOPMENT_MODE: bool = config["system"]["development"] is True

DB_PARAMS: Dict[str, Union[str, int]] = {
    "type": config["db"]["type"],
    "host": config["db"]["host"],
    "port": config["db"]["port"],
    "user": config["db"]["user"],
    "password": config["db"]["password"],
    "database": config["db"]["database"],
}


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


LOCAL_SYMBOLS: List[Tuple[str, str]] = collect_unique_symbol_category_pairs(BUCKET)
