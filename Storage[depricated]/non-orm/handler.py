from .mysql import MySQL
from .postgre import Postgre

# Define a dictionary to map database types to their corresponding classes
DB_HANDLERS = {"mysql": MySQL, "postgre": Postgre}


def initialize_db(DB_PARAMS: dict) -> object:
    """
    Initialize a database connection based on the provided parameters.

    Args:
        DB_PARAMS (dict): A dictionary containing the database parameters.
            It should include at least a 'type' key indicating the database type.

    Returns:
        object: An instance of the appropriate database handler class.
            Returns None if the specified database type is not supported.

    Examples:
        DB_PARAMS = {"type": "mysql", "host": "localhost", "user": "username", "password": "password", "database": "mydb"}
        db_handler = initialize_db(DB_PARAMS)
    """
    db_type = DB_PARAMS["type"].lower()

    # Check if the specified database type is supported
    if db_type in DB_HANDLERS:
        db_handler = DB_HANDLERS[db_type](DB_PARAMS)
        return db_handler
    else:
        return None
