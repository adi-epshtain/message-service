"""Logging configuration."""

import json
import logging
import sys
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs JSON-like structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON-like structure.

        Args:
            record: Log record to format.

        Returns:
            JSON-like formatted log string.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": f"{record.module}.{record.funcName}",
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (excluding internal logging fields)
        excluded_fields = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "message", "pathname", "process", "processName", "relativeCreated",
            "thread", "threadName", "exc_info", "exc_text", "stack_info",
        }
        for key, value in record.__dict__.items():
            if key not in excluded_fields and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid adding multiple handlers if logger is already configured
    if logger.handlers:
        return logger

    # Create console handler - use stderr for better compatibility with uvicorn
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Set formatter
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Create shared logger instance
logger = setup_logging()
