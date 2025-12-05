import logging
import sys
from contextvars import ContextVar

import structlog

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def add_trace_id(logger, method_name, event_dict):
    trace_id = trace_id_var.get()
    if trace_id:
        event_dict["trace_id"] = trace_id
    return event_dict


def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_trace_id,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name)


def bind_trace_id(trace_id: str):
    trace_id_var.set(trace_id)


def get_trace_id() -> str | None:
    return trace_id_var.get()
