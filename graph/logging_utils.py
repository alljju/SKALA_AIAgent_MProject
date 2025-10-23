"""Utilities for instrumenting graph node execution with structured logs."""
from __future__ import annotations

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Optional, TypeVar

_FuncT = TypeVar("_FuncT", bound=Callable[..., Any])

LOGGER_NAME = "graph.nodes"
logger = logging.getLogger(LOGGER_NAME)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _extract_state_keys(args: Iterable[Any], kwargs: Dict[str, Any]) -> list[str]:
    """Try to find the node state argument and extract its keys."""
    if "state" in kwargs and isinstance(kwargs["state"], dict):
        return sorted(kwargs["state"].keys())
    if args:
        first = next(iter(args))
        if isinstance(first, dict):
            return sorted(first.keys())
    return []


def _extract_return_keys(result: Any) -> list[str]:
    """Return the top-level keys of the node result if it is a mapping."""
    if isinstance(result, dict):
        return sorted(result.keys())
    return []


def log_node_io(node_name: Optional[str] = None) -> Callable[[_FuncT], _FuncT]:
    """Decorator that logs node start/end timestamps, duration, and payload keys."""

    def decorator(func: _FuncT) -> _FuncT:
        resolved_name = node_name or getattr(func, "__name__", "node")

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                input_keys = _extract_state_keys(args, kwargs)
                logger.info("--> %s start input_keys=%s", resolved_name, input_keys)
                started = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)  # type: ignore[misc]
                except Exception:
                    elapsed_ms = (time.perf_counter() - started) * 1000.0
                    logger.exception("<-- %s error elapsed_ms=%.1f", resolved_name, elapsed_ms)
                    raise
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                return_keys = _extract_return_keys(result)
                logger.info("<-- %s done elapsed_ms=%.1f return_keys=%s", resolved_name, elapsed_ms, return_keys)
                return result

            return async_wrapper  # type: ignore[return-value]

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            input_keys = _extract_state_keys(args, kwargs)
            logger.info("--> %s start input_keys=%s", resolved_name, input_keys)
            started = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception:
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                logger.exception("<-- %s error elapsed_ms=%.1f", resolved_name, elapsed_ms)
                raise
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            return_keys = _extract_return_keys(result)
            logger.info("<-- %s done elapsed_ms=%.1f return_keys=%s", resolved_name, elapsed_ms, return_keys)
            return result

        return sync_wrapper  # type: ignore[return-value]

    return decorator
