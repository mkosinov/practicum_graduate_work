from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import get_settings


def configure_tracer() -> None:
    resource = Resource(
        attributes={"service.name": get_settings().jaeger_service_name}
    )
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=get_settings().jaeger_host,
                agent_port=get_settings().jaeger_port,
            )
        )
    )
