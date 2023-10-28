# Standard Library Imports
import time

# Third-Party Library Imports
import psycopg2
from psycopg2 import Error

# Internal or Custom Imports
from log_config import logger


class Postgre:
    def __init__(self, db_params: dict) -> None:
        """
        Initialize a Postgre instance and connect to the PostgreSQL database.

        Args:
            db_params (dict): A dictionary containing database connection parameters.
        """
        self.conn = None
        self.cursor = None
        self.connect_to_database(db_params)

    def connect_to_database(self, db_params: dict) -> None:
        """
        Connect to the PostgreSQL database.

        Args:
            db_params (dict): A dictionary containing database connection parameters.

        Raises:
            Exception: If the connection fails after multiple retries.
        """
        max_retries = 3
        retry_delay = 5

        for _ in range(max_retries):
            try:
                self.conn = psycopg2.connect(
                    host=db_params["host"],
                    user=db_params["user"],
                    password=db_params["password"],
                    port=db_params["port"],
                    database=db_params["database"],
                )
                self.cursor = self.conn.cursor()
                self.conn.autocommit = True  # Set autocommit mode
                logger.success(
                    f"PostgreSQL Database for {db_params['user']} Connected Successfully!"
                )
                return
            except Error as e:
                logger.error("Error: Could not connect to the database:", e)
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        logger.error("Failed to connect to the database after multiple retries.")
        raise Exception("Failed to connect to the database")

    def execute_scripts(self, sql_script: str, query_type: str) -> None:
        """
        Execute SQL scripts on the database.

        Args:
            sql_script (str): The SQL script to execute.
            query_type (str): The type of query ('post' or 'get').

        Returns:
            list or None: If query_type is 'get', returns the result as a list, otherwise None.
        """
        try:
            self.cursor.execute(sql_script)
            if query_type == "post":
                self.conn.commit()
                logger.success(
                    f"Successfully executed {query_type} query: {sql_script}"
                )
            elif query_type == "get":
                result = self.cursor.fetchall()
                logger.success(
                    f"Successfully executed {query_type} query: {sql_script}"
                )
                return result
            else:
                self.conn.rollback()
                logger.error(f"Invalid query type: {query_type}")

        except Exception as e:
            self.conn.rollback()
            logger.error("Error, could not execute scripts:", e)

    def close_connection(self) -> None:
        """
        Close the database connection if it's open.
        """
        if self.conn:
            self.conn.close()
            logger.success("Database connection closed.")

    def __del__(self) -> None:
        """
        Destructor to ensure the database connection is closed when the object is destroyed.
        """
        self.close_connection()
