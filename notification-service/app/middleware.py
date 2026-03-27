"""
Custom middleware for production features.
"""

import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logging_config import get_logger, bind_request_context

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request IDs to all requests.

    This enables request tracing across microservices and log correlation.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for access in route handlers
        request.state.request_id = request_id

        # Bind to logging context
        bind_request_context(request_id=request_id)

        # Process request
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            # Log unexpected errors
            logger.error(
                "request_failed",
                path=request.url.path,
                method=request.method,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
        finally:
            # Calculate request duration
            duration = time.time() - start_time

            # Log request completion
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code if 'response' in locals() else 500,
                duration_ms=round(duration * 1000, 2)
            )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract user information from authenticated requests
    and add it to the logging context.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Extract user from request state (set by auth dependency)
        user = getattr(request.state, "user", None)

        if user:
            # Bind user context to logs
            bind_request_context(
                user_id=str(user.id),
                user_email=user.email,
                user_role=user.role.value if hasattr(user.role, 'value') else str(user.role)
            )

        response = await call_next(request)
        return response
