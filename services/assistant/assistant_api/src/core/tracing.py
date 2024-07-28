from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.settings import get_settings


def configure_tracer() -> None:
    resource = Resource(attributes={"service.name": "assistant_api"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=get_settings().tracing.tracing_host,
                agent_port=get_settings().tracing.tracing_port,
            )
        )
    )
    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(ConsoleSpanExporter())
    # )


configure_tracer()
