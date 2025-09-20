import logging
import logging.handlers
import os
import re

from app.common.config import settings

# Color codes for console output
COLORS = {
    'reset': "\033[0m",
    'green': "\033[32m",
    'yellow': "\033[33m",
    'blue': "\033[34m",
    'red': "\033[31m",
}


class ColorFormatter(logging.Formatter):
    """Formats log messages with colors for console output"""

    def format(self, record):
        # Map log levels to colors
        level_colors = {
            logging.INFO: COLORS['green'],
            logging.DEBUG: COLORS['yellow'],
            logging.WARNING: COLORS['blue'],
            logging.ERROR: COLORS['red'],
            logging.CRITICAL: COLORS['red'],
        }

        color = level_colors.get(record.levelno, COLORS['reset'])
        record.levelname = f"{color}{record.levelname}{COLORS['reset']}"
        return super().format(record)


class FileFormatter(logging.Formatter):
    """Formats log messages for file output (removes color codes)"""

    def format(self, record):
        message = super().format(record)
        # Remove ANSI color codes
        return re.sub(r'\033\[\d+m', '', message)


# Log format configuration
fmt = "%(asctime)s [%(levelname)s] %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"

# Main logger setup
logger = logging.getLogger(__name__)
logger.propagate = True

# Console handler for colored output
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter(fmt, datefmt))
logger.addHandler(console_handler)

# File handler for persistent logs
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(log_dir, "app.log"),
    maxBytes=5 * 1024 * 1024,  # 5MB max file size
    backupCount=3,  # Keep 3 backup files
)
file_handler.setFormatter(FileFormatter(fmt, datefmt))
logger.addHandler(file_handler)

# Set log level from settings
logger.setLevel(settings.LOG_LEVEL)
