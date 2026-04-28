"""Prebuilt monitoring adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import AdapterOperationError, BasePrebuiltAdapter

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


class PrometheusAdapter(BasePrebuiltAdapter):
    """Adapter that wraps ``prometheus_client`` primitives."""

    name = "prometheus"
    category = "monitoring"

    def __init__(self, **config: Any):
        super().__init__(**config)
        self._registry: Any | None = None
        self._metrics: dict[str, Any] = {}

    def connect(self) -> None:
        prometheus_client = self._require("prometheus_client")

        def _create_registry() -> Any:
            return prometheus_client.CollectorRegistry(auto_describe=True)

        self._registry = self._wrap_errors("connect", _create_registry)
        super().connect()

    def _get_metric(self, key: str, factory: Callable[[Any], Any]) -> Any:
        if key not in self._metrics:
            self.ensure_connected()
            self._metrics[key] = factory(self._registry)
        return self._metrics[key]

    def counter(self, name: str, description: str, labels: Iterable[str] | None = None) -> Any:
        prometheus_client = self._require("prometheus_client")

        def _factory(registry: Any) -> Any:
            return prometheus_client.Counter(name, description, labelnames=list(labels or []), registry=registry)

        return self._get_metric(f"counter:{name}", _factory)

    def gauge(self, name: str, description: str, labels: Iterable[str] | None = None) -> Any:
        prometheus_client = self._require("prometheus_client")

        def _factory(registry: Any) -> Any:
            return prometheus_client.Gauge(name, description, labelnames=list(labels or []), registry=registry)

        return self._get_metric(f"gauge:{name}", _factory)

    def histogram(self, name: str, description: str, buckets: Iterable[float] | None = None) -> Any:
        prometheus_client = self._require("prometheus_client")

        def _factory(registry: Any) -> Any:
            kwargs = {"buckets": list(buckets)} if buckets else {}
            return prometheus_client.Histogram(name, description, registry=registry, **kwargs)

        return self._get_metric(f"histogram:{name}", _factory)

    def push(self, job: str, gateway: str) -> None:
        prometheus_client = self._require("prometheus_client")
        if self._registry is None:
            raise AdapterOperationError("prometheus registry not initialised")
        self._wrap_errors("push", lambda: prometheus_client.push_to_gateway(gateway, job=job, registry=self._registry))


class DatadogAdapter(BasePrebuiltAdapter):
    """Adapter for Datadog metrics/events using the official client."""

    name = "datadog"
    category = "monitoring"

    def __init__(self, *, api_key: str, app_key: str | None = None, **config: Any):
        super().__init__(api_key=api_key, app_key=app_key, **config)
        self._statsd: Any | None = None

    def connect(self) -> None:
        datadog = self._require("datadog")

        def _initialise() -> Any:
            datadog.initialize(api_key=self._config["api_key"], app_key=self._config.get("app_key"), **self._config.get("options", {}))
            return datadog.statsd

        self._statsd = self._wrap_errors("connect", _initialise)
        super().connect()

    def gauge(self, metric: str, value: float, tags: Iterable[str] | None = None, sample_rate: float = 1.0) -> None:
        self.ensure_connected()
        self._wrap_errors("gauge", lambda: self._statsd.gauge(metric, value, tags=list(tags or []), sample_rate=sample_rate))

    def increment(self, metric: str, value: float = 1.0, tags: Iterable[str] | None = None) -> None:
        self.ensure_connected()
        self._wrap_errors("increment", lambda: self._statsd.increment(metric, value=value, tags=list(tags or [])))

    def event(self, title: str, text: str, tags: Iterable[str] | None = None, alert_type: str | None = None) -> None:
        datadog = self._require("datadog")
        self._wrap_errors("event", lambda: datadog.api.Event.create(title=title, text=text, tags=list(tags or []), alert_type=alert_type))


class CustomMonitoringAdapter(BasePrebuiltAdapter):
    """Adapter that lets applications plug in arbitrary callbacks."""

    name = "custom"
    category = "monitoring"

    def __init__(self, **config: Any):
        super().__init__(**config)
        self._callbacks: dict[str, Callable[..., Any]] = {}

    def register(self, metric: str, callback: Callable[..., Any]) -> None:
        self._callbacks[metric] = callback

    def emit(self, metric: str, *args: Any, **kwargs: Any) -> Any:
        callback = self._callbacks.get(metric)
        if callback is None:
            raise AdapterOperationError(f"No callback registered for metric '{metric}'")
        return callback(*args, **kwargs)


__all__ = [
    "CustomMonitoringAdapter",
    "DatadogAdapter",
    "PrometheusAdapter",
]
