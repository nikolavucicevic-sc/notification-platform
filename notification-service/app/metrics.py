"""
Prometheus metrics for monitoring.
Exposes counters, histograms, and gauges for notifications, API requests, and system health.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Notification metrics
notifications_sent_total = Counter(
    'notifications_sent_total',
    'Total number of notifications sent',
    ['channel', 'status']  # Labels: EMAIL/SMS, success/failed
)

notifications_processing_duration = Histogram(
    'notifications_processing_duration_seconds',
    'Time spent processing notifications',
    ['channel']
)

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Queue metrics
redis_queue_depth = Gauge(
    'redis_queue_depth',
    'Current depth of Redis queues',
    ['queue_name']
)

dlq_message_count = Gauge(
    'dlq_message_count',
    'Number of messages in dead letter queue',
    ['channel']
)

# System metrics
active_users = Gauge(
    'active_users_total',
    'Total number of active users'
)

api_keys_total = Gauge(
    'api_keys_total',
    'Total number of active API keys'
)


def metrics_endpoint():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text format.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsMiddleware:
    """
    Middleware to track API request metrics.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint itself
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        status_code = 500  # Default to error

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time

            # Record metrics
            api_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()

            api_request_duration.labels(
                method=method,
                endpoint=path
            ).observe(duration)
