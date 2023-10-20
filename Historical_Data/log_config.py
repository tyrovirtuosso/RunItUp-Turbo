from loguru import logger

# Remove the default handler
logger.remove()

# Add a file handler to log messages to a file with rotation
logger.add(
    "Logs/Historical_Data/Historical_Data_{time:YYYY-MM-DD_HH-mm}.log",
    rotation="1 minute",
    level="INFO",
)

# Log a message to indicate the start of a new run
logger.info("Starting a new run...\n")
