"""
OpenTelemetry distributed tracing configuration.
Instruments FastAPI and exports traces to Jaeger.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_tracing(app, service_name: str = "notification-service"):
    """
    Set up OpenTelemetry tracing with Jaeger exporter.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for tracing
    """
    # Create a resource identifying this service
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    # Set up the tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",  # Docker service name
        agent_port=6831,
    )

    # Add span processor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument requests library for outbound HTTP calls (optional)
    # RequestsInstrumentor().instrument()

    print(f"✅ OpenTelemetry tracing configured for {service_name}")
    print(f"   Traces will be exported to Jaeger at jaeger:6831")


def get_tracer(name: str = "notification-service"):
    """
    Get a tracer instance for manual instrumentation.

    Usage:
        tracer = get_tracer()
        with tracer.start_as_current_span("my-operation"):
            # Your code here
            pass
    """
    return trace.get_tracer(name)
