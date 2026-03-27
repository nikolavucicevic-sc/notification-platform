"""
Structured logging configuration using structlog.

This module sets up structured JSON logging for production use.
Logs include request IDs, user context, and are easily searchable.
"""

import logging
import sys
from typing import Any
import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application-wide context to all log entries."""
    event_dict["service"] = "notification-service"
    event_dict["version"] = "2.0.0"
    return event_dict


def configure_logging(log_level: str = "INFO", json_logs: bool = True):
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON logs (for production). If False, use console format (for development)
    """
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    if json_logs:
        # Production: JSON logs
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ])
    else:
        # Development: Pretty console logs with colors
        processors.extend([
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("user_created", user_id="123", email="user@example.com")
    """
    return structlog.get_logger(name)


# Convenience function for FastAPI requests
def bind_request_context(request_id: str = None, user_id: str = None, **kwargs):
    """
    Bind request-specific context to all subsequent log calls in this context.

    Args:
        request_id: Unique request identifier
        user_id: User ID making the request
        **kwargs: Additional context to bind

    Example:
        bind_request_context(request_id="abc-123", user_id="user-456")
        logger.info("processing_notification")  # Will include request_id and user_id
    """
    context = {}
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    context.update(kwargs)

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**context)


# Example usage:
if __name__ == "__main__":
    # Development mode
    configure_logging(log_level="DEBUG", json_logs=False)
    logger = get_logger(__name__)

    logger.info("service_started", port=8002, environment="development")
    logger.warning("high_queue_depth", queue="email", depth=1000)
    logger.error("database_connection_failed", error="Connection timeout")

    # With request context
    bind_request_context(request_id="req-123", user_id="user-456")
    logger.info("notification_sent", notification_id="notif-789", channel="email")

    print("\n--- Production mode (JSON) ---\n")

    # Production mode
    configure_logging(log_level="INFO", json_logs=True)
    logger = get_logger(__name__)

    logger.info("service_started", port=8002, environment="production")
    logger.error("notification_failed",
                 notification_id="notif-123",
                 channel="email",
                 error="SMTP connection refused")
