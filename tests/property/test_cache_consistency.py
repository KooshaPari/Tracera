"""Property-based tests for cache key generation and TTL consistency.

Tests determinism and structural invariants of CacheService helpers without
requiring a running Redis instance.
"""

from typing import Any

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tests.test_constants import COUNT_THREE
from tracertm.services.cache_service import CACHE_CONFIG, CacheService

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

cache_type_st = st.sampled_from(list(CACHE_CONFIG.keys()))

safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=1,
    max_size=80,
)

kwarg_values = st.one_of(st.none(), safe_text, st.integers(), st.uuids().map(str))
kwargs_st = st.dictionaries(
    st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=20),
    kwarg_values,
    max_size=5,
)


# ---------------------------------------------------------------------------
# Helper to build a CacheService without connecting to Redis
# ---------------------------------------------------------------------------


class _FakeCacheService(CacheService):
    """CacheService subclass that bypasses Redis connection for unit testing key generation."""

    def __init__(self) -> None:
        # Skip the parent __init__ which tries to connect to Redis.
        # We only need the key generation and TTL methods.
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}


def _make_service() -> _FakeCacheService:
    return _FakeCacheService()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.property
class TestCacheKeyDeterminism:
    """Cache key generation is deterministic and structurally valid."""

    @given(cache_type=cache_type_st, kwargs=kwargs_st)
    @settings(max_examples=100)
    def test_key_deterministic(self, cache_type: str, kwargs: dict[str, Any]) -> None:
        """Same inputs always produce the same key."""
        svc = _make_service()
        key1 = svc._generate_key(cache_type, **kwargs)
        key2 = svc._generate_key(cache_type, **kwargs)
        assert key1 == key2

    @given(cache_type=cache_type_st, kwargs=kwargs_st)
    @settings(max_examples=100)
    def test_key_starts_with_tracertm_prefix(self, cache_type: str, kwargs: dict[str, Any]) -> None:
        """All generated keys start with 'tracertm:' prefix."""
        svc = _make_service()
        key = svc._generate_key(cache_type, **kwargs)
        assert key.startswith("tracertm:")

    @given(cache_type=cache_type_st, kwargs=kwargs_st)
    @settings(max_examples=100)
    def test_key_has_three_colon_segments(self, cache_type: str, kwargs: dict[str, Any]) -> None:
        """Generated keys have exactly the format tracertm:<prefix>:<hash>."""
        svc = _make_service()
        key = svc._generate_key(cache_type, **kwargs)
        parts = key.split(":")
        assert len(parts) == COUNT_THREE, f"Expected 3 colon-separated segments, got {len(parts)}: {key}"

    @given(cache_type=cache_type_st, kwargs=kwargs_st)
    @settings(max_examples=100)
    def test_key_hash_is_32_hex_chars(self, cache_type: str, kwargs: dict[str, Any]) -> None:
        """The hash portion of the key is exactly 32 hex characters."""
        svc = _make_service()
        key = svc._generate_key(cache_type, **kwargs)
        hash_part = key.split(":")[-1]
        assert len(hash_part) == 32
        # Verify it's valid hex
        int(hash_part, 16)

    @given(
        cache_type=cache_type_st,
        kwargs_a=kwargs_st,
        kwargs_b=kwargs_st,
    )
    @settings(max_examples=100)
    def test_different_kwargs_produce_different_keys(
        self,
        cache_type: str,
        kwargs_a: dict[str, Any],
        kwargs_b: dict[str, Any],
    ) -> None:
        """Different non-None kwargs produce different keys (collision resistance)."""
        # Filter None values (they are ignored in key generation)
        filtered_a = {k: v for k, v in sorted(kwargs_a.items()) if v is not None}
        filtered_b = {k: v for k, v in sorted(kwargs_b.items()) if v is not None}
        assume(filtered_a != filtered_b)

        svc = _make_service()
        key_a = svc._generate_key(cache_type, **kwargs_a)
        key_b = svc._generate_key(cache_type, **kwargs_b)
        assert key_a != key_b


@pytest.mark.property
class TestCacheKeyNoneFiltering:
    """None values in kwargs are filtered out of key generation."""

    @given(cache_type=cache_type_st, key_name=safe_text)
    @settings(max_examples=100)
    def test_none_kwargs_ignored(self, cache_type: str, key_name: str) -> None:
        """Passing key=None produces the same key as not passing it at all."""
        svc = _make_service()
        key_with_none = svc._generate_key(cache_type, **{key_name: None})
        key_without = svc._generate_key(cache_type)
        assert key_with_none == key_without


@pytest.mark.property
class TestCacheTTLConsistency:
    """TTL values are always positive integers for known types."""

    @given(cache_type=cache_type_st)
    @settings(max_examples=30)
    def test_ttl_positive_for_known_types(self, cache_type: str) -> None:
        """Known cache types always return a positive TTL."""
        svc = _make_service()
        ttl = svc._get_ttl(cache_type)
        assert isinstance(ttl, int)
        assert ttl > 0

    @given(
        cache_type=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L",))).filter(
            lambda s: s not in CACHE_CONFIG,
        ),
    )
    @settings(max_examples=100)
    def test_ttl_defaults_for_unknown_types(self, cache_type: str) -> None:
        """Unknown cache types get the default TTL of 300."""
        svc = _make_service()
        ttl = svc._get_ttl(cache_type)
        assert ttl == 300

    @given(cache_type=cache_type_st)
    @settings(max_examples=30)
    def test_ttl_matches_config(self, cache_type: str) -> None:
        """TTL for known types matches CACHE_CONFIG."""
        svc = _make_service()
        expected = CACHE_CONFIG[cache_type]["ttl"]
        actual = svc._get_ttl(cache_type)
        assert actual == expected


@pytest.mark.property
class TestCacheKeyPrefixConsistency:
    """Cache key prefix matches the config for the cache type."""

    @given(cache_type=cache_type_st)
    @settings(max_examples=30)
    def test_key_prefix_matches_config(self, cache_type: str) -> None:
        """The prefix segment of the key matches CACHE_CONFIG[type]['prefix']."""
        svc = _make_service()
        key = svc._generate_key(cache_type)
        expected_prefix = CACHE_CONFIG[cache_type]["prefix"]
        parts = key.split(":")
        assert parts[1] == expected_prefix
