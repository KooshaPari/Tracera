# Prebuilt Adapter Library

The prebuilt adapter catalogue under `pheno.adapters.prebuilt` ships batteries
included integrations for networking, data, messaging, machine-learning
inference, storage, caching, and monitoring stacks.  All adapters share a
common lifecycle, defer optional dependencies until they are actually used, and
plug directly into the global `AdapterRegistry`.

## Quick Start

```python
from pheno.adapters import register_prebuilt_adapters
from pheno.core.registry.adapters import AdapterType, get_adapter_registry

registry = register_prebuilt_adapters()

# Resolve a requests-based HTTP client
http = registry.create_adapter_instance(AdapterType.HTTP, "requests")
response = http.request("GET", "https://example.com/api")

# Resolve a Redis cache adapter
cache = registry.create_adapter_instance(AdapterType.CACHE, "redis")
cache.set("greeting", b"hello", ttl=60)
```

> **Tip:** each adapter is lazily instantiated.  Optional dependencies such as
> `httpx`, `boto3`, or `prometheus-client` are only imported when the adapter is
> used.  Missing packages raise `MissingDependencyError` with an actionable
> installation hint.

## Adapter Catalogue

| Category | Adapter | Dependencies | Highlights |
| --- | --- | --- | --- |
| HTTP | `requests` | `requests` | Session-based sync client with optional default headers |
|  | `httpx` | `httpx` | Sync + async clients with shared configuration |
|  | `aiohttp` | `aiohttp` | Async session helper with streaming support |
| Database | `postgresql` | `psycopg[binary]` | Connection factory, query helpers, health check |
|  | `redis` | `redis` | Native client wrapper with ping health check |
|  | `sqlite` | stdlib | Little-to-no configuration, optional row factory |
| Message Queue | `nats` | `nats-py` | Async publish/subscribe convenience API |
|  | `rabbitmq` | `pika` | Queue declaration and blocking consume helpers |
|  | `kafka` | `kafka-python` | Producer/consumer bootstrap with flush support |
| ML Inference | `ollama` | `httpx` or `requests` | REST calls against the local Ollama server |
|  | `vllm` | `httpx` or `requests` | Minimal JSON protocol for vLLM HTTP endpoints |
|  | `mlx` | `mlx`, `mlx-lm` | Loads local MLX models with tokenizer helpers |
|  | `openai` | `openai` | Works with both legacy and v1 OpenAI SDKs |
| File Storage | `local` | stdlib | Path-safe local filesystem operations |
|  | `s3` | `boto3` | Thin wrapper over `put_object`/`get_object`/pagination |
|  | `gcs` | `google-cloud-storage` | Blob upload/download helpers |
| Cache | `in_memory` | stdlib | Ordered dict cache with TTL eviction |
|  | `redis` | `redis` | Shared Redis instance with expire helpers |
|  | `memcached` | `pymemcache` | Simple key/value interface |
| Monitoring | `prometheus` | `prometheus-client` | Counter/gauge/histogram factory + push gateway |
|  | `datadog` | `datadog` | Statsd gauges/increments and event publishing |
|  | `custom` | stdlib | Register bespoke callbacks for bespoke metrics |

## Usage Patterns

### HTTP Clients

```python
registry = register_prebuilt_adapters()
client = registry.create_adapter_instance(
    AdapterType.HTTP,
    "httpx",
    timeout=5,
    headers={"User-Agent": "pheno-sdk"},
)

response = client.request("POST", "https://api.service.dev/items", json={"name": "demo"})
print(response.status_code)

# Async usage
async def fetch() -> str:
    async_client = registry.create_adapter_instance(AdapterType.HTTP, "httpx")
    result = await async_client.arequest("GET", "https://api.service.dev/status")
    return result.text
```

### Databases

```python
pg = registry.create_adapter_instance(
    AdapterType.DATABASE,
    "postgresql",
    dsn="postgresql://user:pass@localhost:5432/app",
)

pg.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, body TEXT)")
rows = pg.fetchall("SELECT body FROM notes")

sqlite = registry.create_adapter_instance(AdapterType.DATABASE, "sqlite", path="/tmp/notes.db")
sqlite.execute("INSERT INTO notes(body) VALUES (?)", ("hello",))
```

### Message Queues

```python
from pheno.core.registry.adapters import AdapterType

rabbit = registry.create_adapter_instance(AdapterType.MESSAGE_QUEUE, "rabbitmq")
rabbit.declare_queue("events")
rabbit.publish("events", b"user.signup")

def on_message(payload: bytes) -> None:
    print("received", payload)

rabbit.consume("events", on_message)
```

### ML Inference

```python
ollama = registry.create_adapter_instance(AdapterType.ML, "ollama", model="llama3")
print(ollama.generate("Write a haiku about adapters."))

openai = registry.create_adapter_instance(AdapterType.ML, "openai", api_key="sk-...")
reply = openai.generate("Summarise the health of all services", max_tokens=128)
```

### File Storage

```python
s3 = registry.create_adapter_instance(AdapterType.STORAGE, "s3", bucket="my-bucket")
s3.write("reports/daily.json", b"{}", content_type="application/json")
blob = s3.read("reports/daily.json")

local = registry.create_adapter_instance(AdapterType.STORAGE, "local", root="./artifacts")
local.write("build.log", b"ok")
```

### Caching

```python
cache = registry.create_adapter_instance(AdapterType.CACHE, "in_memory", max_entries=100)
cache.set("token", "abc", ttl=30)
assert cache.get("token") == "abc"

redis_cache = registry.create_adapter_instance(AdapterType.CACHE, "redis")
redis_cache.set("session", b"data", ttl=300)
```

### Monitoring

```python
prom = registry.create_adapter_instance(AdapterType.MONITORING, "prometheus")
requests_total = prom.counter("requests_total", "Total HTTP requests", labels=["method"])
requests_total.labels("GET").inc()

datadog = registry.create_adapter_instance(AdapterType.MONITORING, "datadog", api_key="dd-...", app_key="app-...")
datadog.gauge("service.latency", 123.4, tags=["service:web"])

custom = registry.create_adapter_instance(AdapterType.MONITORING, "custom")
custom.register("audit", lambda payload: print("AUDIT", payload))
custom.emit("audit", {"status": "ok"})
```

## Health Checks & Metadata

Each prebuilt adapter exposes a `describe()` helper (via `BasePrebuiltAdapter`) that
reports the adapter name, category, and effective configuration, making it
trivial to surface adapter inventories in documentation or telemetry dashboards.
Database and cache adapters include lightweight `health_check()` implementations
where possible (for example PostgreSQL executes `SELECT 1`, Redis relies on
`PING`).

## Troubleshooting

- **Missing dependencies** – install the package listed in the catalogue above
  (e.g. `pip install kafka-python`).
- **Async-only adapters** – the `aiohttp` and `nats` adapters expose async-only
  entrypoints (`connect_async`, `arequest`, `close_async`).  Wrap usage inside an
  event loop or leverage an async task runner such as `anyio`.
- **Registry collisions** – pass `replace=True` to `register_prebuilt_adapters`
  when you intentionally want to override an existing adapter registration.

```python
register_prebuilt_adapters(replace=True)
```

## Next Steps

- Extend the registry with project-specific adapters by calling
  `registry.register_adapter(...)` alongside the prebuilt catalogue.
- Integrate adapters into dependency-injection graphs or service factories by
  resolving them once at start-up and reusing the singleton instances the
  registry caches by default.
