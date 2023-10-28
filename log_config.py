"""
Logging configuration Module

Imports:
- logger from loguru: Custom logger for logging messages.

Configuration:
- Remove the default handler: Removes the default handler from the logger.
- Add a file handler: Adds a file handler to log messages to a file with rotation.
    - File path: "Logs/Historical_Data/Historical_Data_{time:YYYY-MM-DD_HH-mm}.log"
    - Rotation: "60 minute" - Rotates the log file every 60 minutes.
    - Level: "INFO" - Sets the log level to INFO.

Logging:
- Log a message to indicate the start of a new run:
    Logs an INFO-level message to indicate the start of a new run.

Please note that the code relies on the loguru library for logging.
"""


from loguru import logger

# Remove the default handler
logger.remove()

# Add a file handler to log messages to a file with rotation
logger.add(
    "logs/Runitup-Turbo_{time:YYYY-MM-DD_HH-mm}.log",
    rotation="60 minute",
    level="INFO",
)

# Log a message to indicate the start of a new run
logger.info("Starting a new run...\n")
