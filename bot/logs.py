from loguru import logger
import sys
from pathlib import Path

LOG_PATH = Path("logs/bot.log")

def setup_bot_logger():
    logger.remove()

    logger.add(
        sys.stdout,
        format="<blue>[BOT]</blue> {time:HH:mm:ss} | {level} | {message}",
        level="INFO",
        enqueue=True,
    )

    logger.add(
        LOG_PATH,
        rotation="100 MB",
        retention="14 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,
    )

    return logger
