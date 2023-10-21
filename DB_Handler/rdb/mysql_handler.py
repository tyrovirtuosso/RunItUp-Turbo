# System and Environment
import time

# Third-party Libraries
from typing import Dict, List, Optional

# Database
import mysql.connector
from mysql.connector import Error

# Custom Packages
from log_config import logger


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

    def execute_post_query(
        self, query: str, data: Optional[List[tuple]] = None
    ) -> None:
        """
        Execute a post (insert/update) query with optional data.

        Args:
            query (str): The SQL query to execute.
            data (Optional[List[tuple]]): Optional data to execute a parameterized query.

        Returns:
            None
        """
        if data:
            self.cursor.executemany(query, data)
        else:
            self.cursor.execute(query)

        self.conn.commit()
        logger.success(f"Successfully executed post query: {query}")

    def execute_get_query(self, query: str) -> List[tuple]:
        """
        Execute a get (select) query and return the results.

        Args:
            query (str): The SQL query to execute for fetching data.

        Returns:
            List[tuple]: A list of tuples containing the query results.
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        logger.success(f"Successfully executed get query: {query}")
        return result

    def create_tables(self, table_creation_queries) -> None:
        """
        Create database tables based on provided SQL queries.

        This method executes a series of SQL queries to create the necessary database tables for the application.
        The tables are related to storing various data, including price-related information, metadata, categories,
        symbols, strategies, and trading data.

        Args:
            table_creation_queries (list of str): A list of SQL queries used to create the database tables.

        Returns:
            None: This method doesn't return any values; it creates the database tables in place.

        Note: If the tables already exist, they will not be re-created. Unique constraints are defined to ensure data integrity.
        """
        # SQL queries to create database tables (as defined in the method)

        for query in table_creation_queries:
            self.cursor.execute(query)
        self.conn.commit()

        logger.success(
            "Successfully Created or Ignored if already present, MYSQL tables"
        )

    def update_tables(self, table_update_queries) -> None:
        """
        Update database tables based on provided SQL queries.

        This method updates the database tables to incorporate new metadata entries, set symbol and category IDs,
        and insert new strategies (if applicable). It executes a series of SQL queries to perform these updates
        and commits the changes to the database.

        Args:
            table_update_queries (list of str): A list of SQL queries used to update the database tables.

        Returns:
            None: This method doesn't return any values; it updates the tables in place.

        If there is an error while accessing the database or executing queries, an error message is printed.
        """
        # SQL queries to update database tables (as defined in the method)

        for query in table_update_queries:
            self.cursor.execute(query)
        self.conn.commit()

        logger.success("Successfully Updated MYSQL tables")

    def view_all_tables(self) -> None:
        """
        View and display information about all tables in the database.

        This method retrieves and prints information about all tables in the connected database. It displays
        the table names, field specifications (including field name, type, nullability, key, default, and extra),
        and the number of rows in each table.

        Returns:
            None: This method doesn't return any values; it prints table information to the console.

        If there is an error while accessing the database or executing queries, an error message is printed.
        """
        try:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            for table in tables:
                table_name = table[0]
                print(f"\nTable Name: {table_name}")

                # Retrieve table specifications
                self.cursor.execute(f"DESCRIBE {table_name}")
                table_specifications = self.cursor.fetchall()
                for spec in table_specifications:
                    print(
                        f"Field: {spec[0]}, Type: {spec[1]}, Null: {spec[2]}, Key: {spec[3]}, Default: {spec[4]}, Extra: {spec[5]}"
                    )

                # Retrieve the number of rows
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]
                print(f"Number of Rows: {row_count}")

        except Error as e:
            print(f"Error: {e}")
