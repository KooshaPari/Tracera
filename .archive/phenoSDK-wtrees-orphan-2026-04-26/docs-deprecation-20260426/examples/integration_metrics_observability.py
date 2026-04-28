#!/usr/bin/env python3
"""
Integration Example: Metrics + All Modules (Complete Observability)

This example demonstrates comprehensive observability by integrating advanced
metrics with all other extracted modules:
- Context Folding metrics
- Routing decision metrics
- Protocol optimization metrics
- Multi-agent performance metrics
- End-to-end system health monitoring

Use Case:
---------
A production LLM application with complete observability:
1. Track every optimization and decision
2. Monitor performance across all components
3. Detect anomalies automatically
4. Export to multiple monitoring backends
5. Generate real-time dashboards

Benefits:
---------
- Complete visibility into system behavior
- Proactive anomaly detection
- Multi-backend metric export
- Cost and quality tracking
- Production-ready monitoring

Author: Pheno SDK Team
License: MIT
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

# All module imports
from pheno.llm.optimization.context_folding import ContextFolder, FoldingConfig
from pheno.llm.protocol.optimization import OptimizedProtocol, ProtocolConfig, Request, get_protocol
from pheno.llm.routing.ensemble import (
    EnsembleConfig,
    EnsembleMethod,
    EnsembleRouter,
    RoutingContext,
)

# Metrics and backends
from pheno.observability.metrics.advanced import (
    AlertSeverity,
    CloudWatchBackend,
    DatadogBackend,
    OpenTelemetryBackend,
    PrometheusBackend,
    get_metrics_collector,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock Infrastructure
# ============================================================================


class MockTokenizer:
    def encode(self, text: str) -> List[int]:
        return list(range(len(text.split())))

    def decode(self, tokens: List[int]) -> str:
        return f"[{len(tokens)} tokens]"


class MockLLMClient:
    async def complete(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {
            "content": f"Response from {model}",
            "input_tokens": len(prompt.split()) * 2,
            "output_tokens": 100,
            "model": model,
        }


class MockModelRegistry:
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        return {
            "gpt-4": {"cost_per_1k_tokens": 0.03, "quality_score": 0.95, "speed_score": 0.6},
            "gpt-3.5-turbo": {
                "cost_per_1k_tokens": 0.002,
                "quality_score": 0.85,
                "speed_score": 0.95,
            },
        }.get(model, {})


# ============================================================================
# Observable LLM Service with Complete Metrics
# ============================================================================


class ObservableLLMService:
    """LLM service with comprehensive observability.

    This service demonstrates:
    - Metrics collection at every layer
    - Multi-backend export capabilities
    - Automatic anomaly detection
    - Real-time dashboards
    - Cost and quality tracking
    """

    def __init__(self):
        # Initialize core components
        self.tokenizer = MockTokenizer()
        self.llm_client = MockLLMClient()
        self.model_registry = MockModelRegistry()

        # Context folder with metrics
        self.context_folder = ContextFolder(
            config=FoldingConfig(target_compression_ratio=0.5),
            tokenizer=self.tokenizer,
            logger=logger,
        )

        # Router with metrics
        self.router = EnsembleRouter(
            config=EnsembleConfig(
                enabled_strategies=[
                    EnsembleMethod.COST_OPTIMIZED,
                    EnsembleMethod.QUALITY_FIRST,
                    EnsembleMethod.BALANCED,
                ],
            ),
            model_registry=self.model_registry,
            logger=logger,
        )

        # Protocol with metrics
        self.protocol = get_protocol(
            config=ProtocolConfig(
                batching_enabled=True,
                compression_enabled=True,
                pool_size=20,
            ),
            logger=logger,
        )

        # Metrics collector
        self.metrics = get_metrics_collector()

        # Configure anomaly thresholds
        self.metrics.configure_thresholds(
            {
                "token_savings_min_pct": 20.0,  # Minimum 20% savings from context folding
                "compression_ratio_min": 0.4,  # Minimum 40% compression
                "quality_min": 0.7,  # Minimum quality score
                "latency_max_ms": 2000.0,  # Maximum 2s latency
                "success_rate_min_pct": 95.0,  # Minimum 95% success rate
            }
        )

        # Initialize monitoring backends
        self.prometheus = PrometheusBackend(endpoint="http://localhost:9091")
        self.otlp = OpenTelemetryBackend(endpoint="http://localhost:4318")

    async def process_request(
        self,
        prompt: str,
        user_id: str = "anonymous",
    ) -> Dict[str, Any]:
        """Process a request with complete observability.

        Tracks metrics at every step:
        1. Context folding metrics
        2. Routing decision metrics
        3. Protocol optimization metrics
        4. LLM performance metrics
        5. End-to-end latency metrics
        """
        request_id = f"req-{datetime.now().timestamp()}"
        start_time = asyncio.get_event_loop().time()

        logger.info(f"Processing request {request_id}")

        # ===== Step 1: Context Folding with Metrics =====
        original_tokens = len(self.tokenizer.encode(prompt))

        folding_start = asyncio.get_event_loop().time()
        folding_result = await self.context_folder.fold_context(
            context=prompt,
            task_description="User query",
        )
        folding_time = (asyncio.get_event_loop().time() - folding_start) * 1000

        folded_prompt = folding_result.folded_context
        folded_tokens = len(self.tokenizer.encode(folded_prompt))
        tokens_saved = original_tokens - folded_tokens

        # Record folding metrics
        self.metrics.record_token_usage(
            input_tokens=original_tokens,
            output_tokens=0,
            model="context_folder",
            cache_hit=False,
        )

        logger.info(
            f"Context folded: {original_tokens} → {folded_tokens} tokens "
            f"({tokens_saved} saved, {folding_result.statistics.compression_ratio:.2%} compression)"
        )

        # ===== Step 2: Routing with Metrics =====
        routing_start = asyncio.get_event_loop().time()
        routing_result = await self.router.route(
            context=RoutingContext(
                prompt=folded_prompt,
                task_type="general",
                user_id=user_id,
                max_tokens=2048,
            ),
            candidate_models=["gpt-4", "gpt-3.5-turbo"],
        )
        routing_time = (asyncio.get_event_loop().time() - routing_start) * 1000

        selected_model = routing_result.selected_model

        # Record routing metrics
        self.metrics.record_routing_decision(
            selected_model=selected_model,
            confidence=routing_result.confidence,
            routing_time_ms=routing_time,
            method_votes=routing_result.method_votes,
        )

        logger.info(f"Routed to {selected_model} " f"(confidence: {routing_result.confidence:.2%})")

        # ===== Step 3: Protocol Optimization with Metrics =====
        request = Request(
            id=request_id,
            payload={"prompt": folded_prompt, "model": selected_model},
            priority=1,
            timestamp=datetime.now(),
        )

        async def llm_callback(req: Request) -> Any:
            return await self.llm_client.complete(
                prompt=req.payload["prompt"],
                model=req.payload["model"],
            )

        protocol_start = asyncio.get_event_loop().time()
        llm_response = await self.protocol.send(request, callback=llm_callback)
        protocol_time = (asyncio.get_event_loop().time() - protocol_start) * 1000

        # Get protocol stats
        protocol_stats = self.protocol.get_statistics()

        logger.info(f"Protocol processing completed in {protocol_time:.2f}ms")

        # ===== Step 4: LLM Response Metrics =====
        self.metrics.record_token_usage(
            input_tokens=llm_response["input_tokens"],
            output_tokens=llm_response["output_tokens"],
            model=selected_model,
            cache_hit=False,
        )

        # ===== Step 5: End-to-End Performance Metrics =====
        total_time = (asyncio.get_event_loop().time() - start_time) * 1000

        self.metrics.record_performance(
            latency_ms=total_time,
            success=True,
        )

        # ===== Step 6: Quality Metrics =====
        # In production, calculate actual quality metrics
        quality_score = routing_result.confidence * 0.9
        relevance = 0.95
        accuracy = 0.88

        self.metrics.record_quality_metrics(
            quality_score=quality_score,
            relevance=relevance,
            accuracy=accuracy,
            confidence=routing_result.confidence,
        )

        # ===== Step 7: Check for Anomalies =====
        alerts = self.metrics.get_alerts(severity=AlertSeverity.WARNING)
        if alerts:
            logger.warning(f"Found {len(alerts)} alerts during processing")
            for alert in alerts:
                logger.warning(f"Alert: {alert.message} (severity: {alert.severity})")

        # ===== Return Comprehensive Result =====
        return {
            "request_id": request_id,
            "answer": llm_response["content"],
            "model_used": selected_model,
            "metrics": {
                "context_folding": {
                    "original_tokens": original_tokens,
                    "folded_tokens": folded_tokens,
                    "tokens_saved": tokens_saved,
                    "compression_ratio": folding_result.statistics.compression_ratio,
                    "time_ms": folding_time,
                },
                "routing": {
                    "selected_model": selected_model,
                    "confidence": routing_result.confidence,
                    "time_ms": routing_time,
                    "method_votes": routing_result.method_votes,
                },
                "protocol": {
                    "time_ms": protocol_time,
                    "batched": protocol_stats.get("batcher", {}).get("batches_processed", 0) > 0,
                    "compressed": protocol_stats.get("compressor", {}).get("total_compressed", 0)
                    > 0,
                },
                "llm": {
                    "input_tokens": llm_response["input_tokens"],
                    "output_tokens": llm_response["output_tokens"],
                },
                "quality": {
                    "score": quality_score,
                    "relevance": relevance,
                    "accuracy": accuracy,
                },
                "performance": {
                    "total_time_ms": total_time,
                    "breakdown": {
                        "folding_ms": folding_time,
                        "routing_ms": routing_time,
                        "protocol_ms": protocol_time,
                    },
                },
            },
            "alerts": [{"message": a.message, "severity": a.severity.name} for a in alerts],
        }

    async def export_metrics_to_all_backends(self) -> Dict[str, Any]:
        """
        Export metrics to all configured backends.
        """
        metrics = self.metrics.export_metrics()

        results = {}

        # Export to Prometheus
        try:
            await self.prometheus.push(metrics, job="llm_service")
            results["prometheus"] = "success"
        except Exception as e:
            logger.error(f"Prometheus export failed: {e}")
            results["prometheus"] = f"failed: {e}"

        # Export to OpenTelemetry
        try:
            await self.otlp.push(metrics)
            results["opentelemetry"] = "success"
        except Exception as e:
            logger.error(f"OpenTelemetry export failed: {e}")
            results["opentelemetry"] = f"failed: {e}"

        return results

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data formatted for dashboards.
        """
        return self.metrics.get_dashboard_data()


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """
    Run the comprehensive observability example.
    """

    service = ObservableLLMService()

    print("\n" + "=" * 80)
    print("COMPREHENSIVE OBSERVABILITY - Metrics Integration")
    print("=" * 80)

    # Example 1: Process requests with full metrics tracking
    print("\n[1] Processing requests with complete metrics...")

    queries = [
        "Explain quantum computing in simple terms",
        "What are the applications of machine learning in healthcare?",
        "How does blockchain technology work?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query[:50]}...")
        result = await service.process_request(query)

        print(f"  Model: {result['model_used']}")
        print(f"  Quality: {result['metrics']['quality']['score']:.2%}")
        print(f"  Total time: {result['metrics']['performance']['total_time_ms']:.2f}ms")
        print(f"  Tokens saved: {result['metrics']['context_folding']['tokens_saved']}")
        print(f"  Compression: {result['metrics']['context_folding']['compression_ratio']:.2%}")
        print(f"  Alerts: {len(result['alerts'])}")

    # Example 2: View aggregated metrics
    print("\n" + "=" * 80)
    print("[2] Aggregated Metrics Summary")
    print("=" * 80)

    summary = service.metrics.get_summary()

    print("\nToken Metrics:")
    tm = summary.get("token_metrics", {})
    print(f"  Total tokens: {tm.get('total_tokens', 0)}")
    print(f"  Tokens saved: {tm.get('tokens_saved', 0)}")
    print(f"  Savings percentage: {tm.get('savings_percentage', 0):.2%}")

    print("\nPerformance Metrics:")
    pm = summary.get("performance_metrics", {})
    print(f"  Total requests: {pm.get('total_requests', 0)}")
    print(f"  Success rate: {pm.get('success_rate', 0):.2%}")
    print(f"  Avg latency: {pm.get('avg_latency_ms', 0):.2f}ms")
    print(f"  P95 latency: {pm.get('p95_latency_ms', 0):.2f}ms")
    print(f"  P99 latency: {pm.get('p99_latency_ms', 0):.2f}ms")

    print("\nQuality Metrics:")
    qm = summary.get("quality_metrics", {})
    print(f"  Avg quality: {qm.get('avg_quality', 0):.2%}")
    print(f"  Avg accuracy: {qm.get('avg_accuracy', 0):.2%}")
    print(f"  Avg relevance: {qm.get('avg_relevance', 0):.2%}")

    print("\nRouting Metrics:")
    rm = summary.get("routing_metrics", {})
    print(f"  Avg confidence: {rm.get('avg_confidence', 0):.2%}")
    print(f"  Model distribution:")
    for model, count in rm.get("model_distribution", {}).items():
        print(f"    {model}: {count}")

    # Example 3: Check alerts
    print("\n" + "=" * 80)
    print("[3] Alert Summary")
    print("=" * 80)

    all_alerts = service.metrics.get_alerts()
    print(f"\nTotal alerts: {len(all_alerts)}")

    # Group by severity
    alerts_by_severity = {}
    for alert in all_alerts:
        severity = alert.severity.name
        alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1

    for severity, count in alerts_by_severity.items():
        print(f"  {severity}: {count}")

    # Show recent alerts
    if all_alerts:
        print(f"\nRecent alerts:")
        for alert in all_alerts[-3:]:
            print(f"  [{alert.severity.name}] {alert.message}")

    # Example 4: Export to monitoring backends
    print("\n" + "=" * 80)
    print("[4] Exporting Metrics to Backends")
    print("=" * 80)

    export_results = await service.export_metrics_to_all_backends()

    for backend, status in export_results.items():
        print(f"  {backend}: {status}")

    # Example 5: Dashboard data
    print("\n" + "=" * 80)
    print("[5] Dashboard Data Preview")
    print("=" * 80)

    dashboard = service.get_dashboard_data()

    print("\nDashboard Widgets:")
    print(f"  Token savings trend: {len(dashboard.get('token_savings_trend', []))} data points")
    print(f"  Quality trend: {len(dashboard.get('quality_trend', []))} data points")
    print(f"  Latency trend: {len(dashboard.get('latency_trend', []))} data points")

    print("\n" + "=" * 80)
    print("Comprehensive observability example complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
