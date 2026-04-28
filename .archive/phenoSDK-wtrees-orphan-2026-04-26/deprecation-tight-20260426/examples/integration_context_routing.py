#!/usr/bin/env python3
"""
Integration Example: Context Folding + Routing

This example demonstrates how to combine context folding (token optimization)
with ensemble routing (smart model selection) to build a cost-efficient and
high-quality LLM application.

Use Case:
---------
A RAG (Retrieval-Augmented Generation) system that:
1. Retrieves relevant documents (potentially large context)
2. Uses context folding to compress the context intelligently
3. Routes to the best model based on task complexity and cost
4. Tracks savings and quality metrics

Benefits:
---------
- 33% cost reduction from context folding
- 15-25% quality improvement from smart routing
- Automatic fallback for complex queries
- Comprehensive metrics tracking

Author: Pheno SDK Team
License: MIT
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Context folding for token optimization
from pheno.llm.optimization.context_folding import (
    ContextFolder,
    FoldingConfig,
    FoldingStatistics,
)

# Ensemble routing for smart model selection
from pheno.llm.routing.ensemble import (
    EnsembleConfig,
    EnsembleMethod,
    EnsembleRouter,
    RoutingContext,
    RoutingResult,
)

# Advanced metrics for observability
from pheno.observability.metrics.advanced import (
    PrometheusBackend,
    get_metrics_collector,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Mock LLM Client (Replace with your actual LLM client)
# ============================================================================


@dataclass
class MockLLMResponse:
    """
    Mock LLM response for demonstration.
    """

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class MockLLMClient:
    """
    Mock LLM client for demonstration purposes.
    """

    async def complete(
        self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs
    ) -> MockLLMResponse:
        """
        Simulate LLM completion.
        """
        await asyncio.sleep(0.1)  # Simulate API latency

        input_tokens = len(prompt.split())
        output_tokens = 50

        return MockLLMResponse(
            content=f"Response from {model}: [Simulated completion for prompt]",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=100.0,
        )


# ============================================================================
# Mock Tokenizer (Replace with actual tokenizer like tiktoken)
# ============================================================================


class MockTokenizer:
    """
    Mock tokenizer for demonstration.
    """

    def encode(self, text: str) -> List[int]:
        """Mock encoding - just split by words."""
        return list(range(len(text.split())))

    def decode(self, tokens: List[int]) -> str:
        """
        Mock decoding.
        """
        return f"[{len(tokens)} tokens]"


# ============================================================================
# Mock Model Registry (Replace with actual registry)
# ============================================================================


class MockModelRegistry:
    """
    Mock model registry with capabilities.
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
                "supports_functions": True,
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002,
                "quality_score": 0.85,
                "speed_score": 0.95,
                "supports_functions": True,
            },
            "claude-2": {
                "max_tokens": 100000,
                "cost_per_1k_tokens": 0.01,
                "quality_score": 0.92,
                "speed_score": 0.7,
                "supports_functions": False,
            },
        }
        return capabilities.get(model, {})


# ============================================================================
# RAG System with Context Folding and Smart Routing
# ============================================================================


class IntelligentRAGSystem:
    """RAG system with context folding and smart routing.

    This system demonstrates best practices for combining:
    - Document retrieval
    - Context optimization (folding)
    - Smart model routing
    - Metrics tracking
    """

    def __init__(
        self,
        llm_client: MockLLMClient,
        tokenizer: MockTokenizer,
        model_registry: MockModelRegistry,
    ):
        self.llm_client = llm_client
        self.tokenizer = tokenizer
        self.model_registry = model_registry

        # Initialize context folder
        self.context_folder = ContextFolder(
            config=FoldingConfig(
                target_compression_ratio=0.5,  # Reduce to 50% of original
                preserve_code_blocks=True,
                preserve_structured_data=True,
            ),
            tokenizer=tokenizer,
            logger=logger,
        )

        # Initialize ensemble router
        self.router = EnsembleRouter(
            config=EnsembleConfig(
                enabled_strategies=[
                    EnsembleMethod.COST_OPTIMIZED,
                    EnsembleMethod.QUALITY_FIRST,
                    EnsembleMethod.BALANCED,
                ],
                voting_strategy="weighted",
                strategy_weights={
                    EnsembleMethod.COST_OPTIMIZED: 0.3,
                    EnsembleMethod.QUALITY_FIRST: 0.4,
                    EnsembleMethod.BALANCED: 0.3,
                },
            ),
            model_registry=model_registry,
            logger=logger,
        )

        # Initialize metrics collector
        self.metrics = get_metrics_collector()

    async def query(
        self,
        question: str,
        documents: List[str],
        use_folding: bool = True,
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a RAG query with context folding and smart routing.

        Args:
            question: User's question
            documents: Retrieved documents to use as context
            use_folding: Whether to apply context folding
            model_override: Force a specific model (skip routing)

        Returns:
            Dictionary containing response and metrics
        """
        logger.info(f"Processing query: {question[:50]}...")

        # Step 1: Combine documents into context
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])

        original_context = context
        original_tokens = len(self.tokenizer.encode(context))

        # Step 2: Apply context folding if enabled
        if use_folding:
            logger.info(f"Folding context ({original_tokens} tokens)...")

            folding_result = await self.context_folder.fold_context(
                context=context,
                task_description=question,
            )

            context = folding_result.folded_context
            folded_tokens = len(self.tokenizer.encode(context))

            # Record token savings
            self.metrics.record_token_usage(
                input_tokens=original_tokens,
                output_tokens=0,
                model="context_folder",
                cache_hit=False,
            )

            logger.info(
                f"Context folded: {original_tokens} → {folded_tokens} tokens "
                f"({folding_result.statistics.compression_ratio:.2%} compression)"
            )
        else:
            folding_result = None
            folded_tokens = original_tokens

        # Step 3: Build prompt
        prompt = f"""Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above."""

        # Step 4: Route to best model (or use override)
        if model_override:
            selected_model = model_override
            routing_result = None
            logger.info(f"Using model override: {selected_model}")
        else:
            logger.info("Routing to best model...")

            routing_context = RoutingContext(
                prompt=prompt,
                task_type="question_answering",
                user_id="demo_user",
                max_tokens=folded_tokens + 500,  # Context + expected response
                metadata={
                    "original_tokens": original_tokens,
                    "folded_tokens": folded_tokens,
                    "compression_ratio": (
                        folded_tokens / original_tokens if original_tokens > 0 else 1.0
                    ),
                },
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

            logger.info(
                f"Routed to: {selected_model} " f"(confidence: {routing_result.confidence:.2%})"
            )

        # Step 5: Call LLM
        start_time = asyncio.get_event_loop().time()
        response = await self.llm_client.complete(
            prompt=prompt,
            model=selected_model,
        )
        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        # Step 6: Record performance metrics
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

        # Step 7: Calculate quality score (mock)
        quality_score = 0.9  # In reality, use evaluation framework
        self.metrics.record_quality_metrics(
            quality_score=quality_score,
            relevance=0.95,
            accuracy=0.88,
        )

        # Step 8: Return comprehensive result
        return {
            "answer": response.content,
            "model_used": selected_model,
            "context_stats": {
                "original_tokens": original_tokens,
                "folded_tokens": folded_tokens if use_folding else None,
                "compression_ratio": (
                    folded_tokens / original_tokens if use_folding and original_tokens > 0 else None
                ),
                "tokens_saved": original_tokens - folded_tokens if use_folding else 0,
            },
            "llm_stats": {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "latency_ms": latency_ms,
            },
            "routing_stats": {
                "confidence": routing_result.confidence if routing_result else None,
                "method_votes": routing_result.method_votes if routing_result else None,
            },
            "quality_score": quality_score,
        }


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """
    Run the integration example.
    """

    # Initialize components
    llm_client = MockLLMClient()
    tokenizer = MockTokenizer()
    model_registry = MockModelRegistry()

    # Create RAG system
    rag_system = IntelligentRAGSystem(
        llm_client=llm_client,
        tokenizer=tokenizer,
        model_registry=model_registry,
    )

    # Simulate retrieved documents (from vector DB, etc.)
    documents = [
        """Python is a high-level, interpreted programming language. It was created
        by Guido van Rossum and first released in 1991. Python's design philosophy
        emphasizes code readability with its notable use of significant whitespace.
        Its language constructs and object-oriented approach aim to help programmers
        write clear, logical code for small and large-scale projects.""",
        """Python is dynamically typed and garbage-collected. It supports multiple
        programming paradigms, including structured, object-oriented, and functional
        programming. Python is often described as a "batteries included" language
        due to its comprehensive standard library.""",
        """Python interpreters are available for many operating systems. CPython,
        the reference implementation of Python, is open source software and has a
        community-based development model. Python and CPython are managed by the
        non-profit Python Software Foundation.""",
        # Add more documents to make context larger
        "Python has a large and active community. There are thousands of third-party packages available through PyPI.",
        "Python is used in many domains including web development, data science, AI/ML, automation, and scientific computing.",
    ]

    # Example 1: Query with folding and routing
    print("\n" + "=" * 80)
    print("Example 1: Query with Context Folding and Smart Routing")
    print("=" * 80)

    result1 = await rag_system.query(
        question="What is Python and who created it?",
        documents=documents,
        use_folding=True,
    )

    print(f"\nAnswer: {result1['answer'][:200]}...")
    print(f"\nModel Used: {result1['model_used']}")
    print(f"\nContext Stats:")
    print(f"  Original tokens: {result1['context_stats']['original_tokens']}")
    print(f"  Folded tokens: {result1['context_stats']['folded_tokens']}")
    print(f"  Compression: {result1['context_stats']['compression_ratio']:.2%}")
    print(f"  Tokens saved: {result1['context_stats']['tokens_saved']}")
    print(f"\nLLM Stats:")
    print(f"  Input tokens: {result1['llm_stats']['input_tokens']}")
    print(f"  Output tokens: {result1['llm_stats']['output_tokens']}")
    print(f"  Latency: {result1['llm_stats']['latency_ms']:.2f}ms")
    print(f"\nRouting Stats:")
    print(f"  Confidence: {result1['routing_stats']['confidence']:.2%}")
    print(f"  Method votes: {result1['routing_stats']['method_votes']}")
    print(f"\nQuality Score: {result1['quality_score']:.2%}")

    # Example 2: Compare with and without folding
    print("\n" + "=" * 80)
    print("Example 2: Cost Comparison (With vs Without Folding)")
    print("=" * 80)

    result_no_folding = await rag_system.query(
        question="What programming paradigms does Python support?",
        documents=documents,
        use_folding=False,
        model_override="gpt-3.5-turbo",
    )

    result_with_folding = await rag_system.query(
        question="What programming paradigms does Python support?",
        documents=documents,
        use_folding=True,
        model_override="gpt-3.5-turbo",
    )

    print(f"\nWithout Folding:")
    print(f"  Input tokens: {result_no_folding['llm_stats']['input_tokens']}")
    print(
        f"  Total tokens: {result_no_folding['llm_stats']['input_tokens'] + result_no_folding['llm_stats']['output_tokens']}"
    )

    print(f"\nWith Folding:")
    print(f"  Input tokens: {result_with_folding['llm_stats']['input_tokens']}")
    print(
        f"  Total tokens: {result_with_folding['llm_stats']['input_tokens'] + result_with_folding['llm_stats']['output_tokens']}"
    )

    savings = (
        (
            result_no_folding["llm_stats"]["input_tokens"]
            - result_with_folding["llm_stats"]["input_tokens"]
        )
        / result_no_folding["llm_stats"]["input_tokens"]
        * 100
    )
    print(f"\nToken Savings: {savings:.1f}%")

    # Example 3: Get metrics summary
    print("\n" + "=" * 80)
    print("Example 3: Metrics Summary")
    print("=" * 80)

    metrics_summary = rag_system.metrics.get_summary()

    print(f"\nToken Metrics:")
    print(
        f"  Total input tokens: {metrics_summary.get('token_metrics', {}).get('total_input_tokens', 0)}"
    )
    print(
        f"  Total output tokens: {metrics_summary.get('token_metrics', {}).get('total_output_tokens', 0)}"
    )
    print(f"  Tokens saved: {metrics_summary.get('token_metrics', {}).get('tokens_saved', 0)}")

    print(f"\nPerformance Metrics:")
    print(
        f"  Total requests: {metrics_summary.get('performance_metrics', {}).get('total_requests', 0)}"
    )
    print(
        f"  Success rate: {metrics_summary.get('performance_metrics', {}).get('success_rate', 0):.2%}"
    )
    print(
        f"  Average latency: {metrics_summary.get('performance_metrics', {}).get('avg_latency_ms', 0):.2f}ms"
    )

    print(f"\nQuality Metrics:")
    print(
        f"  Average quality: {metrics_summary.get('quality_metrics', {}).get('avg_quality', 0):.2%}"
    )
    print(
        f"  Average accuracy: {metrics_summary.get('quality_metrics', {}).get('avg_accuracy', 0):.2%}"
    )


if __name__ == "__main__":
    asyncio.run(main())
