# Storage Kit

## At a Glance
- **Purpose:** Unified async interface for cloud and local storage providers.
- **Best For:** Managing uploads, downloads, presigned URLs, and metadata across S3, GCS, Azure, local FS, and in-memory storage.
- **Key Building Blocks:** `StorageClient`, provider interfaces (`BaseStorageProvider`), lifecycle hooks, streaming utilities.

## Core Capabilities
- Provider abstraction with consistent API for storing, fetching, listing, and deleting objects.
- Async streaming uploads/downloads with optional chunking.
- Presigned URL generation for temporary access.
- Metadata management and content-type handling.
- Lifecycle policies, retention hooks, and encryption helpers.
- In-memory and filesystem providers for testing and local development.

## Getting Started

### Installation
```
pip install storage-kit
# Extras
pip install "storage-kit[s3]" "storage-kit[gcs]" "storage-kit[azure]"
```

### Minimal Example
```python
from storage_kit import StorageClient
from storage_kit.providers.base import LocalStorageProvider

client = StorageClient(LocalStorageProvider(base_path="./storage"))
await client.upload("docs/report.txt", b"Hello")
data = await client.download("docs/report.txt")
```

## How It Works
- `StorageClient` wraps a provider implementing `BaseStorageProvider` (`providers/base.py`).
- Providers implement `upload`, `download`, `delete`, `exists`, `list`, `get_url` (when supported).
- Backends under `providers` include S3, GCS, Azure, local filesystem, and in-memory.
- Lifecycle module offers hooks for retention policies, archiving, and versioning.
- Streams utilities support large file handling via async generators.

## Usage Recipes
- Generate presigned URLs for S3:
  ```python
  from storage_kit.providers.s3 import S3StorageProvider
  client = StorageClient(S3StorageProvider(bucket="docs"))
  url = await client.get_url("reports/q1.pdf", expires_in=900)
  ```
- Use in-memory provider for tests and swap with real provider via adapter-kit container.
- Encrypt objects using security helpers before uploading sensitive data.
- Trigger event-kit notifications when lifecycle hooks (delete/archive) fire.

## Interoperability
- Works with config-kit to load provider credentials and bucket names.
- Integrates with workflow-kit to orchestrate ingestion pipelines (e.g., file upload → vector embedding).
- Observability-kit instruments storage operations for latency/throughput metrics.

## Operations & Observability
- Emit metrics: `storage_upload_bytes_total`, `storage_operations_total`.
- Configure retries/backoff at provider level to handle transient cloud errors.
- Use lifecycle hooks to enforce retention policies and automatically archive stale content.

## Testing & QA
- `InMemoryStorageProvider` and temporary directories keep tests fast and isolated.
- Snapshot metadata to ensure consistent storage behaviour across providers.
- Contract tests validate provider implementations; see `tests/test_providers.py`.

## Troubleshooting
- **Credential failures:** double-check environment variables or config-kit settings.
- **Presigned URL expiry:** adjust `expires_in` or refresh links before expiry.
- **Streaming issues:** ensure event loop is running and chunk sizes align with provider limits.

## Primary API Surface
- `StorageClient(provider)`
- `await StorageClient.upload(key, data, *, content_type=None, metadata=None)`
- `await StorageClient.download(key)`
- `await StorageClient.delete(key)`
- `await StorageClient.list(prefix=None)`
- `await StorageClient.get_url(key, expires_in)`
- Providers: `providers.s3.S3StorageProvider`, `providers.gcs.GCSStorageProvider`, `providers.azure.AzureBlobStorageProvider`, `providers.base.LocalStorageProvider`, `providers.base.InMemoryStorageProvider`

## Additional Resources
- Examples: `storage-kit/examples/`
- Tests: `storage-kit/tests/`
- Related concepts: [Architecture](../concepts/architecture.md), [Operations](../guides/operations.md)
