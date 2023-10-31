# Standard Library Imports
import json
import os
from typing import Optional

import telegram

# Third-party Library Imports
from dotenv import load_dotenv

from log_config import logger

# Local Imports
from Runitup.constants import TELEGRAM_NOTIFICATION_FILE_PATH


async def send_to_telegram(msg: Optional[str] = None):
    """
    Send a message to a Telegram user or send a database update notification.

    Args:
        msg (str, optional): The message to send to the user. If None, a database update notification is sent.

    Raises:
        Exception: If there is an issue with sending the message.

    """

    load_dotenv()
    TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")

    bot = telegram.Bot(token=TELEGRAM_API_KEY)
    if msg:
        await bot.send_message(chat_id=TELEGRAM_USER_ID, text=msg)
    else:
        if not os.path.exists(TELEGRAM_NOTIFICATION_FILE_PATH):
            # Create an empty dictionary
            notifications = {}

            # Save the empty dictionary to create the file
            with open(TELEGRAM_NOTIFICATION_FILE_PATH, "w") as file:
                json.dump(notifications, file, indent=4)
        else:
            # File exists, load the content
            with open(TELEGRAM_NOTIFICATION_FILE_PATH, "r") as file:
                notifications = json.load(file)

        # message = f"Symbols:\n{notifications['symbols']}\n\n"
        message = "Database Updated Successfully!\n"
        message += f"Symbol Count: {notifications['symbol_count']}\n"
        message += f"Last Update: {notifications['last_update']}\n"
        message += f"Database Size: {notifications['db_size']}\n"

        await bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)
        logger.success("Sent Telegram Notification")
