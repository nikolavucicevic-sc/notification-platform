import logging
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON for easy parsing."""

    SKIP_KEYS = {
        "args", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "message",
        "module", "msecs", "msg", "name", "pathname", "process",
        "processName", "relativeCreated", "stack_info", "taskName",
        "thread", "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "sms-sender",
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in self.SKIP_KEYS:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def configure_logging(log_level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    for noisy in ("httpx", "httpcore", "urllib3", "requests"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


class LoggerAdapter(logging.LoggerAdapter):
    """Wraps standard logger to accept keyword arguments as structured fields."""

    def info(self, msg, *args, **kwargs):
        extra = {**self.extra, **kwargs}
        super().info(msg, *args, extra=extra)

    def error(self, msg, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", False)
        extra = {**self.extra, **kwargs}
        super().error(msg, *args, extra=extra, exc_info=exc_info)

    def warning(self, msg, *args, **kwargs):
        extra = {**self.extra, **kwargs}
        super().warning(msg, *args, extra=extra)

    def debug(self, msg, *args, **kwargs):
        extra = {**self.extra, **kwargs}
        super().debug(msg, *args, extra=extra)


def get_logger(name: str) -> LoggerAdapter:
    return LoggerAdapter(logging.getLogger(name), {})
