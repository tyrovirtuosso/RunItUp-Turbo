# System and Environment
import time

# Third-party Libraries
from typing import Dict

# Database
import mysql.connector
from mysql.connector import Error

# Custom Packages
from log_config import logger


# To-Do
class MySQL:
    def __init__(self, db_params: Dict[str, str]) -> None:
        """
        Initialize a connection to a MySQL database using the provided parameters.

        Args:
            db_params (Dict[str, str]): A dictionary containing the following parameters:
                - 'type': The type of the database (not used in the code).
                - 'host': The host address of the MySQL server.
                - 'port': The port number to connect to the MySQL server.
                - 'user': The username to access the database.
                - 'password': The password for the specified user.
                - 'database': The name of the database to connect to.

        The constructor attempts to establish a connection to the MySQL database using the provided parameters.
        It also creates and updates tables and logs successful or failed connections.

        Raises:
            Error: If there is an error while connecting to the database, an error is raised.

        """
        connected = False
        while not connected:
            try:
                self.conn = mysql.connector.connect(
                    host=db_params["host"],
                    user=db_params["user"],
                    password=db_params["password"],
                    port=db_params["port"],
                    database=db_params["database"],
                )
                self.cursor = self.conn.cursor()
                connected = True
                logger.success(
                    f"MYSQL Database for {db_params['user']} Connected Successfully!"
                )
            except Error as e:
                sleep_time = 5
                logger.error("Error, cannot connect to AWS db:", e)
                logger.info(f"trying again after {sleep_time} seconds")
                time.sleep(sleep_time)
