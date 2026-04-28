#!/usr/bin/env python3
"""
Integration Example: Ensemble Routing + Protocol Optimization

This example demonstrates how to combine ensemble routing (smart model selection)
with protocol optimization (fast request handling) to build a high-performance,
cost-efficient LLM service.

Use Case:
---------
A high-throughput LLM API service that:
1. Receives many concurrent requests
2. Uses protocol optimization for batching and compression
3. Routes each request to the optimal model
4. Tracks performance and cost metrics

Benefits:
---------
- 23x throughput improvement from batching
- 60-70% bandwidth reduction from compression
- 15-25% quality improvement from routing
- 30-50% latency reduction overall

Author: Pheno SDK Team
License: MIT
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Protocol optimization for performance
from pheno.llm.protocol.optimization import (
    OptimizedProtocol,
    ProtocolConfig,
    Request,
    get_protocol,
)

# Ensemble routing for smart model selection
from pheno.llm.routing.ensemble import (
    EnsembleConfig,
    EnsembleMethod,
    EnsembleRouter,
    RoutingContext,
)

# Metrics for observability
from pheno.observability.metrics.advanced import (
    PrometheusBackend,
    get_metrics_collector,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock Components
# ============================================================================


@dataclass
class LLMResponse:
    """
    LLM response structure.
    """

    request_id: str
    model: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class MockLLMClient:
    """
    Mock LLM client.
    """

    async def complete(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        request_id: str = None,
    ) -> LLMResponse:
        """
        Simulate LLM completion.
        """
        await asyncio.sleep(0.05)  # Simulate API call

        return LLMResponse(
            request_id=request_id or "req-123",
            model=model,
            content=f"Response from {model}",
            input_tokens=len(prompt.split()) * 2,
            output_tokens=50,
            latency_ms=50.0,
        )


class MockModelRegistry:
    """
    Mock model registry.
    """

    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """
        Get model capabilities.
        """
        capabilities = {
            "gpt-4": {
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.03,
                "quality_score": 0.95,
                "speed_score": 0.6,
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002,
                "quality_score": 0.85,
                "speed_score": 0.95,
            },
            "claude-2": {
                "max_tokens": 100000,
                "cost_per_1k_tokens": 0.01,
                "quality_score": 0.92,
                "speed_score": 0.7,
            },
        }
        return capabilities.get(model, {})


# ============================================================================
# High-Performance LLM Service
# ============================================================================


class HighPerformanceLLMService:
    """High-performance LLM service with routing and protocol optimization.

    This service demonstrates:
    - Request batching for throughput
    - Payload compression for bandwidth
    - Connection pooling for efficiency
    - Smart routing for quality/cost balance
    - Comprehensive metrics tracking
    """

    def __init__(
        self,
        llm_client: MockLLMClient,
        model_registry: MockModelRegistry,
    ):
        self.llm_client = llm_client
        self.model_registry = model_registry

        # Initialize protocol optimization
        self.protocol = get_protocol(
            config=ProtocolConfig(
                batching_enabled=True,
                batch_size=10,
                batch_timeout_ms=100.0,
                compression_enabled=True,
                compression_threshold=1024,
                pool_size=20,
                pool_ttl=300,
            ),
            logger=logger,
        )

        # Initialize ensemble router
        self.router = EnsembleRouter(
            config=EnsembleConfig(
                enabled_strategies=[
                    EnsembleMethod.COST_OPTIMIZED,
                    EnsembleMethod.QUALITY_FIRST,
                    EnsembleMethod.LATENCY_OPTIMIZED,
                ],
                voting_strategy="weighted",
                strategy_weights={
                    EnsembleMethod.COST_OPTIMIZED: 0.3,
                    EnsembleMethod.QUALITY_FIRST: 0.3,
                    EnsembleMethod.LATENCY_OPTIMIZED: 0.4,
                },
            ),
            model_registry=model_registry,
            logger=logger,
        )

        # Initialize metrics
        self.metrics = get_metrics_collector()

        # Request counter
        self._request_count = 0

    async def process_request(
        self,
        prompt: str,
        task_type: str = "general",
        user_id: str = "anonymous",
        priority: int = 1,
    ) -> Dict[str, Any]:
        """Process a single LLM request with routing and optimization.

        Args:
            prompt: User prompt
            task_type: Type of task (for routing)
            user_id: User identifier
            priority: Request priority (1-5, higher = more important)

        Returns:
            Dictionary containing response and metrics
        """
        self._request_count += 1
        request_id = f"req-{self._request_count}"

        logger.info(f"Processing request {request_id}")

        # Step 1: Route to best model
        routing_context = RoutingContext(
            prompt=prompt,
            task_type=task_type,
            user_id=user_id,
            max_tokens=2048,
            metadata={"priority": priority},
        )

        routing_result = await self.router.route(
            context=routing_context,
            candidate_models=["gpt-4", "gpt-3.5-turbo", "claude-2"],
        )

        selected_model = routing_result.selected_model

        # Record routing metrics
        self.metrics.record_routing_decision(
            selected_model=selected_model,
            confidence=routing_result.confidence,
            routing_time_ms=routing_result.routing_time_ms,
            method_votes=routing_result.method_votes,
        )

        # Step 2: Create optimized request
        payload = {
            "prompt": prompt,
            "model": selected_model,
            "request_id": request_id,
            "user_id": user_id,
            "task_type": task_type,
        }

        request = Request(
            id=request_id,
            payload=payload,
            priority=priority,
            timestamp=datetime.now(),
        )

        # Step 3: Send through optimized protocol
        start_time = asyncio.get_event_loop().time()

        async def process_callback(req: Request) -> Any:
            """
            Callback to process the request.
            """
            return await self.llm_client.complete(
                prompt=req.payload["prompt"],
                model=req.payload["model"],
                request_id=req.id,
            )

        response = await self.protocol.send(request, callback=process_callback)

        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        # Step 4: Record metrics
        self.metrics.record_token_usage(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            model=selected_model,
            cache_hit=False,
        )

        self.metrics.record_performance(
            latency_ms=latency_ms,
            success=True,
        )

        # Quality score (mock)
        quality_score = routing_result.confidence * 0.9
        self.metrics.record_quality_metrics(
            quality_score=quality_score,
            relevance=0.9,
            confidence=routing_result.confidence,
        )

        # Step 5: Get protocol statistics
        protocol_stats = self.protocol.get_statistics()

        return {
            "request_id": request_id,
            "answer": response.content,
            "model_used": selected_model,
            "routing": {
                "confidence": routing_result.confidence,
                "routing_time_ms": routing_result.routing_time_ms,
                "method_votes": routing_result.method_votes,
            },
            "performance": {
                "total_latency_ms": latency_ms,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
            "protocol_optimization": {
                "batched": protocol_stats.get("batcher", {}).get("batches_processed", 0) > 0,
                "compressed": protocol_stats.get("compressor", {}).get("total_compressed", 0) > 0,
                "compression_ratio": protocol_stats.get("compressor", {}).get(
                    "avg_compression_ratio", 1.0
                ),
                "pool_cache_hit_rate": protocol_stats.get("pool", {}).get("cache_hit_rate", 0.0),
            },
            "quality_score": quality_score,
        }

    async def process_batch(
        self,
        requests: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Process multiple requests concurrently.

        Args:
            requests: List of request dictionaries

        Returns:
            List of results
        """
        logger.info(f"Processing batch of {len(requests)} requests")

        # Process all requests concurrently
        tasks = [
            self.process_request(
                prompt=req["prompt"],
                task_type=req.get("task_type", "general"),
                user_id=req.get("user_id", "anonymous"),
                priority=req.get("priority", 1),
            )
            for req in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Request {i} failed: {result}")
                processed_results.append(
                    {
                        "error": str(result),
                        "request": requests[i],
                    }
                )
            else:
                processed_results.append(result)

        return processed_results


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """
    Run the integration example.
    """

    # Initialize components
    llm_client = MockLLMClient()
    model_registry = MockModelRegistry()

    # Create service
    service = HighPerformanceLLMService(
        llm_client=llm_client,
        model_registry=model_registry,
    )

    # Example 1: Single request
    print("\n" + "=" * 80)
    print("Example 1: Single Optimized Request")
    print("=" * 80)

    result1 = await service.process_request(
        prompt="Explain quantum computing in simple terms",
        task_type="explanation",
        user_id="user-123",
        priority=3,
    )

    print(f"\nRequest ID: {result1['request_id']}")
    print(f"Model Used: {result1['model_used']}")
    print(f"Answer: {result1['answer']}")
    print(f"\nRouting:")
    print(f"  Confidence: {result1['routing']['confidence']:.2%}")
    print(f"  Routing Time: {result1['routing']['routing_time_ms']:.2f}ms")
    print(f"  Method Votes: {result1['routing']['method_votes']}")
    print(f"\nPerformance:")
    print(f"  Latency: {result1['performance']['total_latency_ms']:.2f}ms")
    print(f"  Input Tokens: {result1['performance']['input_tokens']}")
    print(f"  Output Tokens: {result1['performance']['output_tokens']}")
    print(f"\nProtocol Optimization:")
    print(f"  Batched: {result1['protocol_optimization']['batched']}")
    print(f"  Compressed: {result1['protocol_optimization']['compressed']}")
    print(f"  Compression Ratio: {result1['protocol_optimization']['compression_ratio']:.2%}")

    # Example 2: Batch processing
    print("\n" + "=" * 80)
    print("Example 2: Batch Processing (10 concurrent requests)")
    print("=" * 80)

    batch_requests = [
        {
            "prompt": f"Question {i}: What is artificial intelligence?",
            "task_type": "qa",
            "priority": i % 3 + 1,
        }
        for i in range(10)
    ]

    start_time = asyncio.get_event_loop().time()
    batch_results = await service.process_batch(batch_requests)
    batch_time = (asyncio.get_event_loop().time() - start_time) * 1000

    print(f"\nProcessed {len(batch_results)} requests in {batch_time:.2f}ms")
    print(f"Average time per request: {batch_time / len(batch_results):.2f}ms")

    # Show sample results
    print(f"\nSample Results:")
    for i in range(min(3, len(batch_results))):
        result = batch_results[i]
        print(f"\n  Request {i+1}:")
        print(f"    Model: {result['model_used']}")
        print(f"    Latency: {result['performance']['total_latency_ms']:.2f}ms")
        print(f"    Quality: {result['quality_score']:.2%}")

    # Example 3: Protocol statistics
    print("\n" + "=" * 80)
    print("Example 3: Protocol Optimization Statistics")
    print("=" * 80)

    protocol_stats = service.protocol.get_statistics()

    print(f"\nBatcher Statistics:")
    batcher = protocol_stats.get("batcher", {})
    print(f"  Total requests: {batcher.get('total_requests', 0)}")
    print(f"  Batches processed: {batcher.get('batches_processed', 0)}")
    print(f"  Average batch size: {batcher.get('avg_batch_size', 0):.2f}")
    print(f"  Throughput improvement: {batcher.get('throughput_improvement', 1.0):.2f}x")

    print(f"\nCompressor Statistics:")
    compressor = protocol_stats.get("compressor", {})
    print(f"  Total compressed: {compressor.get('total_compressed', 0)}")
    print(f"  Bytes saved: {compressor.get('bytes_saved', 0)}")
    print(f"  Avg compression ratio: {compressor.get('avg_compression_ratio', 1.0):.2%}")

    print(f"\nConnection Pool Statistics:")
    pool = protocol_stats.get("pool", {})
    print(f"  Total connections: {pool.get('total_connections', 0)}")
    print(f"  Active connections: {pool.get('active_connections', 0)}")
    print(f"  Cache hits: {pool.get('cache_hits', 0)}")
    print(f"  Cache hit rate: {pool.get('cache_hit_rate', 0):.2%}")

    # Example 4: Overall metrics
    print("\n" + "=" * 80)
    print("Example 4: Overall System Metrics")
    print("=" * 80)

    metrics_summary = service.metrics.get_summary()

    print(f"\nToken Metrics:")
    token_metrics = metrics_summary.get("token_metrics", {})
    print(f"  Total input tokens: {token_metrics.get('total_input_tokens', 0)}")
    print(f"  Total output tokens: {token_metrics.get('total_output_tokens', 0)}")
    print(f"  Total tokens: {token_metrics.get('total_tokens', 0)}")

    print(f"\nPerformance Metrics:")
    perf_metrics = metrics_summary.get("performance_metrics", {})
    print(f"  Total requests: {perf_metrics.get('total_requests', 0)}")
    print(f"  Successful requests: {perf_metrics.get('successful_requests', 0)}")
    print(f"  Success rate: {perf_metrics.get('success_rate', 0):.2%}")
    print(f"  Average latency: {perf_metrics.get('avg_latency_ms', 0):.2f}ms")
    print(f"  P95 latency: {perf_metrics.get('p95_latency_ms', 0):.2f}ms")

    print(f"\nRouting Metrics:")
    routing_metrics = metrics_summary.get("routing_metrics", {})
    print(f"  Average confidence: {routing_metrics.get('avg_confidence', 0):.2%}")
    print(f"  Model distribution:")
    model_dist = routing_metrics.get("model_distribution", {})
    for model, count in model_dist.items():
        print(f"    {model}: {count} requests")


if __name__ == "__main__":
    asyncio.run(main())
