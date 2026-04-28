#!/usr/bin/env python3
"""
Integration Example: Refactoring Patterns + All Modules

This example demonstrates how to use refactoring patterns to extract and
reorganize code while integrating with all other modules to maintain
functionality and observability.

Use Case:
---------
Refactoring a monolithic LLM application into hexagonal architecture:
1. Extract domain logic into pure functions
2. Create port interfaces for external dependencies
3. Build adapters for specific implementations
4. Integrate with routing, optimization, and metrics
5. Validate architecture compliance

Benefits:
---------
- Cleaner separation of concerns
- Easier testing with mocked dependencies
- Better maintainability
- Integration with optimization modules
- Comprehensive metrics tracking

Author: Pheno SDK Team
License: MIT
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

from pheno.llm.optimization.context_folding import ContextFolder, FoldingConfig

# Integration with other modules
from pheno.llm.routing.ensemble import (
    EnsembleConfig,
    EnsembleMethod,
    EnsembleRouter,
    RoutingContext,
)
from pheno.observability.metrics.advanced import get_metrics_collector

# Refactoring patterns
from pheno.patterns.refactoring.analyzer import analyze_architecture
from pheno.patterns.refactoring.extractor import extract_to_port

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# BEFORE: Monolithic Code (Tightly Coupled)
# ============================================================================


class MonolithicLLMApp:
    """
    BEFORE: A monolithic LLM application with tight coupling.

    Problems:
    - Direct dependencies on specific implementations
    - Hard to test without real API calls
    - Difficult to swap implementations
    - No separation between domain and infrastructure
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.request_count = 0

    async def process_query(self, query: str) -> str:
        """
        Process a query (tightly coupled implementation).
        """
        self.request_count += 1

        # Hardcoded OpenAI API call
        # In reality, this would use openai.ChatCompletion.create()
        await asyncio.sleep(0.1)  # Simulate API call
        response = f"Response to: {query}"

        # Hardcoded logging
        print(f"[{datetime.now()}] Query processed: {query[:30]}...")

        # Hardcoded caching logic mixed with business logic
        # cache.set(query, response)

        return response


# ============================================================================
# AFTER: Hexagonal Architecture (Decoupled)
# ============================================================================

# ===== PORTS (Interfaces) =====


class LLMClientPort(Protocol):
    """
    Port for LLM client.
    """

    async def complete(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Complete a prompt.
        """
        ...


class CachePort(Protocol):
    """
    Port for caching.
    """

    async def get(self, key: str) -> Optional[Any]:
        """
        Get from cache.
        """
        ...

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set in cache.
        """
        ...


class MetricsPort(Protocol):
    """
    Port for metrics.
    """

    def record_request(self, query: str, latency_ms: float, success: bool) -> None:
        """
        Record request metrics.
        """
        ...


class LoggerPort(Protocol):
    """
    Port for logging.
    """

    def info(self, message: str) -> None:
        """
        Log info message.
        """
        ...


# ===== DOMAIN LAYER (Pure Business Logic) =====


@dataclass
class QueryRequest:
    """
    Domain model for a query request.
    """

    query: str
    user_id: str
    context: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class QueryResponse:
    """
    Domain model for a query response.
    """

    answer: str
    model_used: str
    tokens_used: int
    latency_ms: float
    cached: bool


class QueryProcessor:
    """Domain service for processing queries.

    This is pure business logic with no infrastructure dependencies. All external
    dependencies are injected through ports.
    """

    def __init__(
        self,
        llm_client: LLMClientPort,
        cache: CachePort,
        metrics: MetricsPort,
        logger: LoggerPort,
    ):
        self.llm_client = llm_client
        self.cache = cache
        self.metrics = metrics
        self.logger = logger

    async def process(self, request: QueryRequest) -> QueryResponse:
        """Process a query request.

        This is pure business logic - no direct dependencies on
        specific implementations.
        """
        start_time = asyncio.get_event_loop().time()

        self.logger.info(f"Processing query: {request.query[:50]}...")

        # Check cache
        cache_key = f"query:{request.query}"
        cached_response = await self.cache.get(cache_key)

        if cached_response:
            self.logger.info("Cache hit!")
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self.metrics.record_request(request.query, latency_ms, success=True)

            return QueryResponse(
                answer=cached_response["answer"],
                model_used=cached_response["model"],
                tokens_used=cached_response["tokens"],
                latency_ms=latency_ms,
                cached=True,
            )

        # Call LLM
        try:
            llm_response = await self.llm_client.complete(
                prompt=request.query,
                model="gpt-3.5-turbo",
            )

            # Cache response
            await self.cache.set(
                cache_key,
                {
                    "answer": llm_response["content"],
                    "model": llm_response["model"],
                    "tokens": llm_response.get("input_tokens", 0)
                    + llm_response.get("output_tokens", 0),
                },
                ttl=3600,
            )

            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self.metrics.record_request(request.query, latency_ms, success=True)

            return QueryResponse(
                answer=llm_response["content"],
                model_used=llm_response["model"],
                tokens_used=llm_response.get("input_tokens", 0)
                + llm_response.get("output_tokens", 0),
                latency_ms=latency_ms,
                cached=False,
            )

        except Exception as e:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self.logger.info(f"Error processing query: {e}")
            self.metrics.record_request(request.query, latency_ms, success=False)
            raise


# ===== ADAPTERS (Infrastructure Implementations) =====


class MockLLMAdapter:
    """
    Adapter for mock LLM (for testing or demo).
    """

    async def complete(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Complete with mock LLM.
        """
        await asyncio.sleep(0.05)  # Simulate API latency
        return {
            "content": f"Mock response to: {prompt[:50]}...",
            "model": model,
            "input_tokens": len(prompt.split()) * 2,
            "output_tokens": 100,
        }


class OptimizedLLMAdapter:
    """Adapter that integrates LLM with optimization modules.

    This adapter combines:
    - Context folding for token optimization
    - Ensemble routing for model selection
    - Protocol optimization for performance
    """

    def __init__(self):
        # Initialize optimization components
        self.context_folder = ContextFolder(
            config=FoldingConfig(target_compression_ratio=0.5),
            tokenizer=MockTokenizer(),
            logger=logger,
        )

        self.router = EnsembleRouter(
            config=EnsembleConfig(
                enabled_strategies=[
                    EnsembleMethod.COST_OPTIMIZED,
                    EnsembleMethod.BALANCED,
                ],
            ),
            model_registry=MockModelRegistry(),
            logger=logger,
        )

        self.llm_client = MockLLMClient()

    async def complete(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Complete with optimizations.
        """
        # Fold context
        folding_result = await self.context_folder.fold_context(
            context=prompt,
            task_description="Query processing",
        )

        # Route to best model
        routing_result = await self.router.route(
            context=RoutingContext(
                prompt=folding_result.folded_context,
                task_type="general",
                user_id="default",
                max_tokens=2048,
            ),
            candidate_models=["gpt-4", "gpt-3.5-turbo"],
        )

        # Call LLM
        response = await self.llm_client.complete(
            prompt=folding_result.folded_context,
            model=routing_result.selected_model,
        )

        return response


class InMemoryCacheAdapter:
    """
    Simple in-memory cache adapter.
    """

    def __init__(self):
        self.cache: Dict[str, Any] = {}

    async def get(self, key: str) -> Optional[Any]:
        """
        Get from cache.
        """
        return self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set in cache.
        """
        self.cache[key] = value


class MetricsAdapter:
    """
    Adapter for advanced metrics.
    """

    def __init__(self):
        self.metrics = get_metrics_collector()

    def record_request(self, query: str, latency_ms: float, success: bool) -> None:
        """
        Record request metrics.
        """
        self.metrics.record_performance(latency_ms=latency_ms, success=success)


class LoggerAdapter:
    """
    Adapter for Python logging.
    """

    def __init__(self):
        self.logger = logging.getLogger("QueryProcessor")

    def info(self, message: str) -> None:
        """
        Log info message.
        """
        self.logger.info(message)


# ===== Mock Components =====


class MockTokenizer:
    def encode(self, text: str) -> List[int]:
        return list(range(len(text.split())))


class MockModelRegistry:
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        return {
            "gpt-4": {"cost_per_1k_tokens": 0.03, "quality_score": 0.95},
            "gpt-3.5-turbo": {"cost_per_1k_tokens": 0.002, "quality_score": 0.85},
        }.get(model, {})


class MockLLMClient:
    async def complete(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {
            "content": f"Response from {model}",
            "model": model,
            "input_tokens": len(prompt.split()) * 2,
            "output_tokens": 100,
        }


# ============================================================================
# Example Usage: Demonstrating Refactoring Benefits
# ============================================================================


async def main():
    """
    Demonstrate refactoring patterns integration.
    """

    print("\n" + "=" * 80)
    print("REFACTORING PATTERNS INTEGRATION")
    print("=" * 80)

    # Example 1: Basic setup with mock adapter
    print("\n[1] Basic Hexagonal Architecture Setup")
    print("-" * 80)

    processor_basic = QueryProcessor(
        llm_client=MockLLMAdapter(),
        cache=InMemoryCacheAdapter(),
        metrics=MetricsAdapter(),
        logger=LoggerAdapter(),
    )

    request = QueryRequest(
        query="What is machine learning?",
        user_id="user-123",
    )

    result = await processor_basic.process(request)

    print(f"Answer: {result.answer}")
    print(f"Model: {result.model_used}")
    print(f"Latency: {result.latency_ms:.2f}ms")
    print(f"Cached: {result.cached}")

    # Example 2: With optimized adapter (context folding + routing)
    print("\n[2] With Optimization Integration")
    print("-" * 80)

    processor_optimized = QueryProcessor(
        llm_client=OptimizedLLMAdapter(),
        cache=InMemoryCacheAdapter(),
        metrics=MetricsAdapter(),
        logger=LoggerAdapter(),
    )

    request = QueryRequest(
        query="Explain quantum computing and its applications in cryptography, including detailed technical explanations",
        user_id="user-456",
    )

    result = await processor_optimized.process(request)

    print(f"Answer: {result.answer}")
    print(f"Model: {result.model_used}")
    print(f"Tokens: {result.tokens_used}")
    print(f"Latency: {result.latency_ms:.2f}ms")

    # Example 3: Test caching
    print("\n[3] Testing Cache Hit")
    print("-" * 80)

    # Second request (should hit cache)
    result_cached = await processor_optimized.process(request)

    print(f"Cached: {result_cached.cached}")
    print(f"Latency (cached): {result_cached.latency_ms:.2f}ms")

    # Example 4: Compare architectures
    print("\n[4] Architecture Comparison")
    print("-" * 80)

    print("\nMonolithic Architecture Problems:")
    print("  - Tight coupling to specific implementations")
    print("  - Hard to test (requires real API calls)")
    print("  - Difficult to swap components")
    print("  - Mixed business and infrastructure logic")

    print("\nHexagonal Architecture Benefits:")
    print("  - Clean separation of concerns")
    print("  - Easy to test with mocks")
    print("  - Simple to swap implementations")
    print("  - Pure business logic in domain layer")
    print("  - Integration with optimization modules")

    print("\n[5] Metrics Summary")
    print("-" * 80)

    metrics = processor_optimized.metrics.metrics.get_summary()

    perf = metrics.get("performance_metrics", {})
    print(f"\nPerformance:")
    print(f"  Total requests: {perf.get('total_requests', 0)}")
    print(f"  Success rate: {perf.get('success_rate', 0):.2%}")
    print(f"  Avg latency: {perf.get('avg_latency_ms', 0):.2f}ms")

    print("\n" + "=" * 80)
    print("Refactoring patterns integration complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
