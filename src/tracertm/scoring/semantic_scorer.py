#!/usr/bin/env python3
"""tracera/semantic_scorer.py

DAG-T6: Semantic-embedding scorer for the Tracera requirements-traceability
pipeline. Sits alongside the existing jaccard + tfidf scorers in
`src/tracertm/scoring/`. Computes cosine similarity between the
requirement text and the coverage/trace text using a small embedding model
(so it runs on a single 3090 Ti).

Strategy
--------
1. Lazy-import `sentence_transformers` and load a small model
   (`all-MiniLM-L6-v2` — 80MB, ~50ms per short-text pair on a 3090 Ti).
2. If `sentence_transformers` is unavailable (sandboxed CI), fall back to a
   deterministic hashed-bag-of-words embedding (the lexical fallback also
   useful as a "lexical prior" for the score blend).
3. Score one requirement against one trace: return a float in [0, 1].
4. The class is intentionally lightweight: a single `SemanticScorer.score`
   method so it can be plugged into the existing scoring registry as
   `register("semantic", SemanticScorer())`.

USAGE:

    from tracertm.scoring.semantic_scorer import SemanticScorer
    s = SemanticScorer()
    print(s.score("JWT auth required", "Add JWT-based authentication"))

The scorer degrades gracefully — running it without `sentence_transformers`
yields the hashed-bow fallback, which is still useful for unit tests and
CI environments that don't have the model installed.
"""
from __future__ import annotations

import hashlib
import math
import re
import struct
from dataclasses import dataclass
from typing import Iterable, Sequence

# Tokenisation: split on non-alphanumerics, lowercase, drop empty.
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(s: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(s) if t]


def _hash_token(tok: str, dim: int) -> int:
    """Deterministically map a token to one of `dim` buckets."""
    h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
    (val,) = struct.unpack("<Q", h)
    return val % dim


def hashed_bow(text: str, dim: int = 256) -> list[float]:
    """A tiny, deterministic bag-of-words embedding.

    Each unique token contributes +1 (signed by a hash bit) to one of
    `dim` buckets. L2-normalised. Cheap to compute, stable across
    processes, and good enough for a fallback that stays in the same
    ballpark as a real embedding.
    """
    vec = [0.0] * dim
    for tok in _tokenize(text):
        idx = _hash_token(tok, dim)
        # Sign bit (1) flips negative, 0 stays positive. Lets us
        # distinguish "absent" from "present with negative weight".
        sign = -1.0 if (_hash_token(tok + "§sign", 2) == 0) else 1.0
        vec[idx] += sign
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return max(-1.0, min(1.0, dot))


def _try_load_sentence_transformer(model_name: str):
    """Best-effort import; returns None if `sentence_transformers` is missing."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        return None
    return SentenceTransformer(model_name)


@dataclass
class SemanticScorer:
    """Cosine-sim scorer with a graceful lexical fallback.

    The fallback is intentional: CI and lightweight installations should
    still be able to score without pulling 80MB of model weights. The
    `available` property tells callers which path is active.
    """

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dim: int = 256
    _model: object = None  # set in __post_init__ if available
    _uses_real_model: bool = False

    def __post_init__(self) -> None:
        model = _try_load_sentence_transformer(self.model_name)
        if model is not None:
            self._model = model
            self._uses_real_model = True

    @property
    def available(self) -> bool:
        return self._uses_real_model

    def embed(self, text: str) -> list[float]:
        if self._uses_real_model and self._model is not None:
            # `self._model` is a SentenceTransformer; encode returns np.ndarray.
            import numpy as np  # local import — only when model is loaded
            v = self._model.encode([text], normalize_embeddings=True)[0]
            return [float(x) for x in np.asarray(v)]
        return hashed_bow(text, dim=self.dim)

    def score(self, requirement: str, trace: str) -> float:
        """Cosine similarity in [0, 1] between the requirement and the trace.

        Clamps to [0, 1] — negative cosine (orthogonal embeddings) maps to
        0 so the score is comparable to jaccard/tfidf.
        """
        a = self.embed(requirement)
        b = self.embed(trace)
        return max(0.0, cosine(a, b))

    def score_batch(
        self, requirement: str, traces: Iterable[str]
    ) -> list[float]:
        return [self.score(requirement, t) for t in traces]


def register(registry: dict) -> None:
    """Plug into the existing scoring registry.

    Tracera's scoring registry is a `dict[str, Callable[[str, str], float]]`
    populated from `src/tracertm/scoring/__init__.py`. This helper attaches
    a fresh `SemanticScorer` as `registry["semantic"]` so the CLI's
    `--scorer semantic` flag works out of the box.
    """
    s = SemanticScorer()
    registry["semantic"] = s.score
    registry.setdefault("semantic_meta", lambda: {
        "model": s.model_name,
        "available": s.available,
        "dim": s.dim,
    })


if __name__ == "__main__":
    # Smoke test: require no model.
    s = SemanticScorer()
    a = "JWT auth required on /api/* endpoints"
    b = "Add JWT-based authentication to the /api/v1 router"
    c = "Refactor the CLI colour palette"
    print(f"score (a, b) = {s.score(a, b):.3f}  (expect: > 0.5)")
    print(f"score (a, c) = {s.score(a, c):.3f}  (expect: < 0.2)")
    print(f"uses real model: {s.available}")
