import time

import psycopg2
from psycopg2 import Error

# Custom Packages
from log_config import logger


class Postgre:
    def __init__(self, db_params) -> None:
        print(db_params)

        connected = False
        while not connected:
            try:
                self.conn = psycopg2.connect(
                    host=db_params["host"],
                    user=db_params["user"],
                    password=db_params["password"],
                    port=db_params["port"],
                    database=db_params["database"],
                )
                self.cursor = self.conn.cursor()
                connected = True
                logger.success(
                    f"Postgre Database for {db_params['user']} Connected Successfully!"
                )
            except Error as e:
                sleep_time = 5
                logger.error("Error, cannot connect to AWS db:", e)
                logger.info(f"trying again after {sleep_time} seconds")
                time.sleep(sleep_time)

    def execute_scripts(self, sql_script):
        try:
            self.cursor.execute(sql_script)

            # sql_commands = sql_script.split(';')
            # for i in range(len(sql_commands)):
            #     command = sql_commands[i].strip()
            #     command = command + ";"
            #     if i != len(sql_commands) - 1:
            #         self.cursor.execute(command)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error("Error, could not execute scripts:", e)
