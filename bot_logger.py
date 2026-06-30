import logging
import os
from datetime import datetime


def setup_logger():
    """
    Creates and configures the bot logger.
    Logs are saved inside the logs folder.
    """

    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_file_name = datetime.now().strftime("logs/bot_%Y-%m-%d.log")

    logging.basicConfig(
        filename=log_file_name,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s | %(message)s")
    console.setFormatter(formatter)

    logging.getLogger().addHandler(console)

    return logging.getLogger()