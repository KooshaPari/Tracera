"""
ML inference ports for local runtimes such as Ollama, MLX, and vLLM.

The interfaces defined here standardize how the SDK interacts with on-device model
servers providing text generation, embeddings, or model lifecycle management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence


class InferenceTask(StrEnum):
    """Supported inference task categories."""

    CHAT_COMPLETION = "chat_completion"
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"


@dataclass(slots=True)
class GenerationOptions:
    """Common generation parameters supported across runtimes."""

    temperature: float = 0.7
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    stop_sequences: Sequence[str] | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    extra: dict[str, Any] | None = None


@dataclass(slots=True)
class GenerationRequest:
    """Text generation request forwarded to inference engines."""

    model: str
    prompt: str | list[dict[str, str]]
    options: GenerationOptions = field(default_factory=GenerationOptions)
    task: InferenceTask = InferenceTask.CHAT_COMPLETION
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class GenerationChunk:
    """Streaming chunk emitted while generating text."""

    token: str
    index: int
    finished: bool = False
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class GenerationResponse:
    """Aggregated response for non-streaming requests."""

    text: str
    model: str
    tokens_prompt: int | None = None
    tokens_completion: int | None = None
    latency_ms: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class EmbeddingResponse:
    """Response container for embedding generation."""

    vectors: list[list[float]]
    model: str
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class ModelInfo:
    """Describes an available model in the runtime catalog."""

    name: str
    family: str | None = None
    size_mib: float | None = None
    quantization: str | None = None
    capabilities: list[InferenceTask] | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class RuntimeHealth:
    """Health indicator for an inference runtime."""

    healthy: bool
    message: str | None = None
    latency_ms: float | None = None
    last_checked: float | None = None


class TextInferencePort(Protocol):
    """Primary interface for running text inference workloads."""

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a full response without streaming."""
        ...

    async def stream(self, request: GenerationRequest) -> AsyncIterator[GenerationChunk]:
        """Stream partial responses as they are produced."""
        ...

    async def embeddings(
        self,
        inputs: Sequence[str],
        *,
        model: str,
        options: dict[str, Any] | None = None,
    ) -> EmbeddingResponse:
        """Produce vector embeddings for the provided inputs."""
        ...

    async def ensure_model(
        self,
        model: str,
        *,
        keep_warm: bool = True,
    ) -> ModelInfo:
        """Fetch or load ``model`` so it is ready to serve requests."""
        ...

    async def unload_model(self, model: str) -> None:
        """Unload ``model`` to free runtime resources."""
        ...

    async def list_models(self) -> list[ModelInfo]:
        """Return catalog of models currently known to the runtime."""
        ...

    async def health(self) -> RuntimeHealth:
        """Return the latest health information for the runtime."""
        ...


__all__ = [
    "EmbeddingResponse",
    "GenerationChunk",
    "GenerationOptions",
    "GenerationRequest",
    "GenerationResponse",
    "InferenceTask",
    "ModelInfo",
    "RuntimeHealth",
    "TextInferencePort",
]
