"""Prebuilt file storage adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import AdapterOperationError, BasePrebuiltAdapter


class LocalFileStorageAdapter(BasePrebuiltAdapter):
    """Adapter that reads and writes to the local filesystem."""

    name = "local"
    category = "storage"

    def __init__(self, *, root: str | Path, create: bool = True, **config: Any):
        root_path = Path(root).expanduser().resolve()
        if create:
            root_path.mkdir(parents=True, exist_ok=True)
        super().__init__(root=str(root_path), **config)

    def _full_path(self, key: str) -> Path:
        return Path(self._config["root"]).joinpath(key).resolve()

    def write(self, key: str, data: bytes) -> None:
        path = self._full_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_bytes(data)
        except Exception as exc:  # pragma: no cover - filesystem specific
            raise AdapterOperationError(f"Failed to write {key}: {exc}") from exc

    def read(self, key: str) -> bytes:
        path = self._full_path(key)
        try:
            return path.read_bytes()
        except FileNotFoundError:
            raise AdapterOperationError(f"File not found: {key}")

    def delete(self, key: str) -> None:
        path = self._full_path(key)
        try:
            path.unlink(missing_ok=True)
        except AttributeError:  # pragma: no cover - Python <3.8 fallback
            if path.exists():
                path.unlink()

    def list(self, prefix: str = "") -> list[str]:
        root = Path(self._config["root"])
        results: list[str] = []
        for item in root.rglob("*"):
            if item.is_file():
                relative = item.relative_to(root).as_posix()
                if relative.startswith(prefix):
                    results.append(relative)
        return results


class S3StorageAdapter(BasePrebuiltAdapter):
    """Adapter for Amazon S3 using ``boto3``."""

    name = "s3"
    category = "storage"

    def __init__(self, *, bucket: str, **config: Any):
        super().__init__(bucket=bucket, **config)
        self._client: Any | None = None

    def connect(self) -> None:
        boto3 = self._require("boto3")

        def _client() -> Any:
            return boto3.client("s3", **self._config.get("client_options", {}))

        self._client = self._wrap_errors("connect", _client)
        super().connect()

    def write(self, key: str, data: bytes, *, content_type: str | None = None) -> None:
        self.ensure_connected()

        def _put() -> Any:
            kwargs = {"Bucket": self._config["bucket"], "Key": key, "Body": data}
            if content_type:
                kwargs["ContentType"] = content_type
            return self._client.put_object(**kwargs)

        self._wrap_errors("put_object", _put)

    def read(self, key: str) -> bytes:
        self.ensure_connected()

        def _get() -> bytes:
            obj = self._client.get_object(Bucket=self._config["bucket"], Key=key)
            return obj["Body"].read()

        return self._wrap_errors("get_object", _get)

    def delete(self, key: str) -> None:
        self.ensure_connected()
        self._wrap_errors("delete_object", lambda: self._client.delete_object(Bucket=self._config["bucket"], Key=key))

    def list(self, prefix: str = "") -> list[str]:
        self.ensure_connected()
        paginator = self._client.get_paginator("list_objects_v2")
        results: list[str] = []
        for page in paginator.paginate(Bucket=self._config["bucket"], Prefix=prefix):  # pragma: no cover - requires AWS
            for obj in page.get("Contents", []):
                results.append(obj["Key"])
        return results


class GCSStorageAdapter(BasePrebuiltAdapter):
    """Adapter for Google Cloud Storage."""

    name = "gcs"
    category = "storage"

    def __init__(self, *, bucket: str, **config: Any):
        super().__init__(bucket=bucket, **config)
        self._client: Any | None = None

    def connect(self) -> None:
        storage = self._require("google.cloud.storage", install_hint="google-cloud-storage")

        def _client() -> Any:
            return storage.Client(**self._config.get("client_options", {}))

        self._client = self._wrap_errors("connect", _client)
        super().connect()

    def _bucket(self) -> Any:
        if self._client is None:
            raise AdapterOperationError("gcs client not initialised")
        return self._client.bucket(self._config["bucket"])

    def write(self, key: str, data: bytes, *, content_type: str | None = None) -> None:
        bucket = self._bucket()
        blob = bucket.blob(key)
        try:
            blob.upload_from_string(data, content_type=content_type)
        except Exception as exc:  # pragma: no cover - requires GCP
            raise AdapterOperationError(f"gcs upload failed: {exc}") from exc

    def read(self, key: str) -> bytes:
        bucket = self._bucket()
        blob = bucket.blob(key)
        try:
            return blob.download_as_bytes()
        except Exception as exc:  # pragma: no cover
            raise AdapterOperationError(f"gcs read failed: {exc}") from exc

    def delete(self, key: str) -> None:
        bucket = self._bucket()
        blob = bucket.blob(key)
        try:
            blob.delete()
        except Exception as exc:  # pragma: no cover
            raise AdapterOperationError(f"gcs delete failed: {exc}") from exc

    def list(self, prefix: str = "") -> list[str]:
        bucket = self._bucket()
        return [blob.name for blob in bucket.list_blobs(prefix=prefix)]  # pragma: no cover


__all__ = [
    "GCSStorageAdapter",
    "LocalFileStorageAdapter",
    "S3StorageAdapter",
]
