from DB_Handler.rdb.mysql_handler import MySQL

from .constants import DB_PARAMS, DEVELOPMENT_MODE
from .queries import mysql_create_tables, mysql_update_tables

if DEVELOPMENT_MODE:
    if DB_PARAMS["type"].lower() == "mysql":
        db_handler = MySQL(DB_PARAMS)
        db_handler.create_tables(mysql_create_tables)
        db_handler.update_tables(mysql_update_tables)
        print("meow")
