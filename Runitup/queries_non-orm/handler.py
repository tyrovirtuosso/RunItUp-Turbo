from typing import Dict, Optional


def read_sql_file(file_path: str) -> Optional[str]:
    """
    Read the contents of an SQL file and return it as a string.

    Parameters:
    - file_path (str): The path to the SQL file to read.

    Returns:
    - str: The content of the SQL file as a string, or None if the file is not found.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


file_paths = [
    "Runitup/queries/create_table.sql",
    "Runitup/queries/get_symbol_category.sql",
    "Runitup/queries/get_latest_date.sql",
]

sql_scripts: Dict[str, str] = {}

for file_path in file_paths:
    script = read_sql_file(file_path)
    if script is not None:
        sql_scripts[file_path] = script


# You can access your SQL scripts using their file paths as keys in the 'sql_scripts' dictionary.
create_table_script = sql_scripts["Runitup/queries/create_table.sql"]
get_symbol_category_script = sql_scripts["Runitup/queries/get_symbol_category.sql"]
get_latest_date_script = sql_scripts["Runitup/queries/get_latest_date.sql"]
