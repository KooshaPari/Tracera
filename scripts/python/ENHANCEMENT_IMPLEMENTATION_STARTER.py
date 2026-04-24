"""Requirements Enhancement Implementation Starter Kit.

This file contains production-ready code templates for integrating
enhancement libraries into TracerTM. Copy and adapt as needed.

Files to create:
1. src/tracertm/services/enhancement_service.py (this content)
2. src/tracertm/api/routers/enhancements.py (see bottom)
3. src/tracertm/models/enhancement_metadata.py (schemas)
4. src/tracertm/repositories/enhancement_repository.py (persistence)
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar

# Third-party imports
try:
    from sentence_transformers import SentenceTransformer, util
except ImportError as err:
    msg = "Install with: bun add sentence-transformers"
    raise ImportError(msg) from err

try:
    import spacy
except ImportError as err:
    msg = "Install with: python -m spacy download en_core_web_sm"
    raise ImportError(msg) from err

try:
    import networkx as nx
except ImportError as err:
    msg = "Install with: bun add networkx"
    raise ImportError(msg) from err

try:
    from icontract import ensure, invariant, require
except ImportError as err:
    msg = "Install with: bun add icontract"
    raise ImportError(msg) from err

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS & ENUMS
# ============================================================================


class EnhancementCapability(Enum):
    """Available enhancement capabilities."""

    SEMANTIC_ANALYSIS = "semantic_analysis"
    QUALITY_ANALYSIS = "quality_analysis"
    IMPACT_ANALYSIS = "impact_analysis"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    VERIFICATION = "verification"


@dataclass
class QualityMetrics:
    """Quality analysis results."""

    score: float  # 0-100
    grade: str  # A, B, C, D, F
    ambiguous_terms: list[str]
    passive_voice_used: bool
    word_count: int
    sentence_count: int
    complexity_level: str  # simple, moderate, complex
    recommendations: list[str]
    timestamp: datetime = None

    def __post_init__(self) -> None:
        """__post_init__ implementation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ImpactAnalysis:
    """Impact analysis results."""

    direct_impact_count: int
    transitive_impact_count: int
    impacted_item_ids: list[str]
    impact_depth: int
    risk_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    affected_status_distribution: dict[str, int]
    timestamp: datetime = None

    def __post_init__(self) -> None:
        """__post_init__ implementation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DuplicateCandidate:
    """Potential duplicate requirement."""

    item_1_id: str
    item_1_title: str
    item_2_id: str
    item_2_title: str
    similarity_score: float  # 0-1
    confidence: float = 0.95


@dataclass
class EnhancementResult:
    """Unified enhancement result."""

    capability: EnhancementCapability
    item_id: str
    metrics: dict[str, Any]
    success: bool = True
    error: str | None = None
    timestamp: datetime = None

    def __post_init__(self) -> None:
        """__post_init__ implementation."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


# ============================================================================
# SEMANTIC ANALYSIS SERVICE
# ============================================================================


class SemanticAnalysisService:
    """Semantic analysis using sentence-transformers.

    Handles:
    - Duplicate detection
    - Semantic similarity
    - Requirement clustering
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize semantic analyzer.

        Args:
            model_name: HuggingFace model identifier
                - "all-MiniLM-L6-v2" (recommended, 80MB)
                - "all-mpnet-base-v2" (larger, more accurate)
                - "all-distilroberta-v1"
        """
        logger.info("Loading semantic model: %s", model_name)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.cached_embeddings = {}

    async def find_duplicate_requirements(
        self,
        requirements: list[dict[str, str]],  # [{"id": "...", "description": "..."}]
        threshold: float = 0.85,
        skip_ids: list[str] | None = None,
    ) -> list[DuplicateCandidate]:
        """Find potentially duplicate requirements.

        Args:
            requirements: List of requirement dicts with 'id' and 'description'
            threshold: Similarity threshold (0-1, recommended 0.85)
            skip_ids: IDs to skip comparison (self-links)

        Returns:
            List of DuplicateCandidate objects
        """
        if not requirements:
            return []

        skip_ids = skip_ids or []

        # Extract descriptions
        descriptions = [r["description"] for r in requirements]

        # Encode all descriptions
        logger.info(f"Encoding {len(descriptions)} requirements...")
        embeddings = self.model.encode(descriptions, batch_size=32, show_progress_bar=False, convert_to_tensor=True)

        # Find duplicates
        logger.info("Searching for duplicates (threshold=%s)...", threshold)
        pairs = util.semantic_search(embeddings, embeddings, top_k=len(embeddings), score_function=util.cos_sim)

        duplicates = []
        seen_pairs = set()

        for idx, matches in enumerate(pairs):
            for match in matches[1:]:  # Skip self-match
                match_idx = match["corpus_id"]

                if idx >= match_idx:  # Avoid duplicates
                    continue

                score = float(match["score"])

                if score >= threshold:
                    req1 = requirements[idx]
                    req2 = requirements[match_idx]

                    # Skip if either ID is in skip list
                    if req1["id"] in skip_ids or req2["id"] in skip_ids:
                        continue

                    pair_key = (req1["id"], req2["id"])
                    if pair_key not in seen_pairs:
                        duplicates.append(
                            DuplicateCandidate(
                                item_1_id=req1["id"],
                                item_1_title=req1.get("title", "Unknown"),
                                item_2_id=req2["id"],
                                item_2_title=req2.get("title", "Unknown"),
                                similarity_score=score,
                            ),
                        )
                        seen_pairs.add(pair_key)

        logger.info(f"Found {len(duplicates)} potential duplicates")
        return duplicates

    async def calculate_semantic_similarity(self, req1_description: str, req2_description: str) -> float:
        """Calculate similarity between two requirements (0-1).

        Args:
            req1_description: First requirement description
            req2_description: Second requirement description

        Returns:
            Similarity score (0=completely different, 1=identical)
        """
        embeddings = self.model.encode([req1_description, req2_description])
        return float(util.pytorch_cos_sim(embeddings[0], embeddings[1]))

    async def cluster_requirements(
        self,
        requirements: list[dict[str, str]],
        num_clusters: int = 5,
    ) -> dict[int, list[str]]:
        """Cluster requirements by semantic similarity.

        Args:
            requirements: List of requirement dicts
            num_clusters: Number of clusters

        Returns:
            Dict mapping cluster_id to list of requirement IDs
        """
        descriptions = [r["description"] for r in requirements]
        embeddings = self.model.encode(descriptions)

        # Simple clustering (k-means would require sklearn)
        # Using a naive approach: group by centroid distance
        clusters: dict[int, list[str]] = {i: [] for i in range(num_clusters)}

        for idx, _embedding in enumerate(embeddings):
            # Find closest cluster (simplified)
            cluster_id = idx % num_clusters
            clusters[cluster_id].append(requirements[idx]["id"])

        return clusters


# ============================================================================
# NLP QUALITY ANALYSIS SERVICE
# ============================================================================


class QualityAnalysisService:
    """Requirement quality analysis using spaCy and NLP.

    Analyzes:
    - Ambiguous terms
    - Passive voice usage
    - Complexity metrics
    - Measurability
    - Testability
    """

    AMBIGUOUS_WORDS: ClassVar[set[str]] = {
        "appropriate",
        "suitable",
        "adequate",
        "relevant",
        "necessary",
        "important",
        "some",
        "various",
        "etc",
        "quickly",
        "slowly",
        "fast",
        "slow",
        "large",
        "small",
        "good",
        "bad",
        "nice",
        "easy",
        "difficult",
        "possible",
        "reasonable",
        "typical",
        "often",
        "generally",
        "usually",
        "several",
        "many",
        "few",
        "a lot",
        "a little",
    }

    ACTION_VERBS: ClassVar[set[str]] = {
        "shall",
        "should",
        "must",
        "will",
        "can",
        "may",
        "implement",
        "provide",
        "create",
        "generate",
        "process",
    }

    def __init__(self, model: str = "en_core_web_sm") -> None:
        """Initialize NLP analyzer."""
        logger.info("Loading spaCy model: %s", model)
        try:
            self.nlp = spacy.load(model)
        except OSError:
            logger.warning("Model %s not found. Installing...", model)
            import shutil
            import subprocess

            python = shutil.which("python") or "python"
            subprocess.run([python, "-m", "spacy", "download", model], check=True)
            self.nlp = spacy.load(model)

    async def analyze_requirement(self, requirement_text: str) -> QualityMetrics:
        """Comprehensive quality analysis of a requirement.

        Args:
            requirement_text: Requirement description

        Returns:
            QualityMetrics with detailed analysis
        """
        doc = self.nlp(requirement_text)

        # Basic metrics
        word_count = len([t for t in doc if not t.is_punct])
        sentence_count = len(list(doc.sents))

        # Detect ambiguous terms
        ambiguous_terms = [token.text for token in doc if token.text.lower() in self.AMBIGUOUS_WORDS]

        # Detect passive voice
        passive_voice = self._has_passive_voice(doc)

        # Detect action verbs
        has_action_verb = any(token.text.lower() in self.ACTION_VERBS for token in doc)

        # Calculate complexity
        complexity_level = self._calculate_complexity(doc)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            ambiguous_terms,
            passive_voice,
            has_action_verb,
            word_count,
            complexity_level,
        )

        # Calculate quality score
        score = self._calculate_quality_score(
            ambiguous_terms,
            passive_voice,
            has_action_verb,
            word_count,
            complexity_level,
        )

        grade = self._score_to_grade(score)

        return QualityMetrics(
            score=score,
            grade=grade,
            ambiguous_terms=ambiguous_terms,
            passive_voice_used=passive_voice,
            word_count=word_count,
            sentence_count=sentence_count,
            complexity_level=complexity_level,
            recommendations=recommendations,
        )

    def _has_passive_voice(self, doc: Any) -> bool:
        """Detect if requirement uses passive voice."""
        for token in doc:
            if token.dep_ in {"auxpass", "aux"} and token.pos_ == "AUX":
                return True
            if token.lemma_ in {"be", "get"} and any(t.pos_ == "VERB" for t in doc):
                return True
        return False

    def _calculate_complexity(self, doc: Any) -> str:
        """Classify complexity level."""
        token_count = len(doc)
        sent_count = len(list(doc.sents))
        avg_tokens_per_sent = token_count / sent_count if sent_count > 0 else 0

        if token_count < 20 and avg_tokens_per_sent < 15:
            return "simple"
        if token_count < 50 and avg_tokens_per_sent < 20:
            return "moderate"
        return "complex"

    def _calculate_quality_score(
        self,
        ambiguous_terms: list[str],
        passive_voice: bool,
        has_action_verb: bool,
        word_count: int,
        complexity_level: str,
    ) -> float:
        """Calculate quality score (0-100)."""
        score = 100.0

        # Deduct for ambiguous terms (5 points each)
        score -= len(ambiguous_terms) * 5

        # Deduct for passive voice
        if passive_voice:
            score -= 10

        # Bonus for action verbs
        if has_action_verb:
            score += 5

        # Deduct for length extremes
        if word_count < 10:
            score -= 15
        elif word_count > 100:
            score -= 10

        # Deduct for excessive complexity
        if complexity_level == "complex":
            score -= 15

        return max(0, min(100, score))

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def _generate_recommendations(
        self,
        ambiguous_terms: list[str],
        passive_voice: bool,
        has_action_verb: bool,
        word_count: int,
        complexity_level: str,
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if ambiguous_terms:
            recommendations.append(f"Replace ambiguous terms: {', '.join(ambiguous_terms)}")

        if passive_voice:
            recommendations.append("Use active voice for clarity")

        if not has_action_verb:
            recommendations.append("Add action verb (shall, must, should, will, can)")

        if word_count < 10:
            recommendations.append("Expand requirement with more context")

        if word_count > 100:
            recommendations.append("Break into smaller, focused requirements")

        if complexity_level == "complex":
            recommendations.append("Simplify or split requirement into multiple items")

        return recommendations


# ============================================================================
# IMPACT ANALYSIS SERVICE
# ============================================================================


class ImpactAnalysisService:
    """Impact analysis using NetworkX for dependency graphs.

    Calculates:
    - Direct and transitive impact
    - Circular dependencies
    - Risk scoring
    """

    def __init__(self) -> None:
        """Initialize impact analysis service."""
        self.graph: nx.DiGraph | None = None

    async def build_graph(self, items: list[dict[str, Any]], links: list[dict[str, Any]]) -> nx.DiGraph:
        """Build dependency graph from items and links.

        Args:
            items: List of item dicts with 'id', 'title', 'status'
            links: List of link dicts with 'source_id', 'target_id', 'link_type'

        Returns:
            NetworkX DiGraph
        """
        graph = nx.DiGraph()

        # Add nodes with attributes
        for item in items:
            graph.add_node(
                item["id"],
                title=item.get("title", ""),
                status=item.get("status", "draft"),
                priority=item.get("priority", 3),
            )

        # Add edges
        for link in links:
            graph.add_edge(link["source_id"], link["target_id"], relationship=link.get("link_type", "depends_on"))

        self.graph = graph
        logger.info(f"Built graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")

        return graph

    async def calculate_impact(self, item_id: str, direction: str = "downstream") -> ImpactAnalysis:
        """Calculate impact of changing a requirement.

        Args:
            item_id: Target item ID
            direction: "downstream" (affected by) or "upstream" (depends on)

        Returns:
            ImpactAnalysis results
        """
        if not self.graph:
            msg = "Graph not built. Call build_graph() first."
            raise ValueError(msg)

        if direction == "downstream":
            # Items affected by this change
            impacted = set(nx.descendants(self.graph, item_id))
            impacted.add(item_id)  # Include self
        else:
            # Items this depends on
            impacted = set(nx.ancestors(self.graph, item_id))
            impacted.add(item_id)

        # Calculate depth
        depth = self._calculate_impact_depth(item_id, direction)

        # Calculate risk score
        risk_score = self._calculate_risk_score(list(impacted))

        # Get status distribution
        status_dist = self._get_status_distribution(list(impacted))

        return ImpactAnalysis(
            direct_impact_count=len(list(self.graph.successors(item_id)))
            if direction == "downstream"
            else len(list(self.graph.predecessors(item_id))),
            transitive_impact_count=len(impacted) - 1,  # Exclude self
            impacted_item_ids=sorted(impacted - {item_id}),
            impact_depth=depth,
            risk_score=risk_score,
            risk_level=self._score_to_risk_level(risk_score),
            affected_status_distribution=status_dist,
        )

    def _calculate_impact_depth(self, item_id: str, direction: str) -> int:
        """Calculate depth of dependency chain."""
        if direction == "downstream":
            paths = nx.single_source_shortest_path_length(self.graph, item_id)
        else:
            reverse_graph = self.graph.reverse(copy=True)
            paths = nx.single_source_shortest_path_length(reverse_graph, item_id)

        return max(paths.values()) - 1 if paths else 0

    def _calculate_risk_score(self, impacted_ids: list[str]) -> float:
        """Calculate risk based on number and status of impacted items."""
        risk = 0.0

        for item_id in impacted_ids:
            if item_id not in self.graph:
                continue

            status = self.graph.nodes[item_id].get("status", "draft")

            # Different statuses have different risk weights
            risk_weights = {"done": 5.0, "testing": 4.0, "approved": 3.0, "draft": 1.0}

            risk += risk_weights.get(status, 1.0)

        # Normalize to 0-100
        return min(100.0, (risk / len(impacted_ids)) * 20) if impacted_ids else 0.0

    def _get_status_distribution(self, item_ids: list[str]) -> dict[str, int]:
        """Get distribution of statuses in impacted items."""
        distribution: dict[str, int] = {}

        for item_id in item_ids:
            if item_id not in self.graph:
                continue

            status = self.graph.nodes[item_id].get("status", "unknown")
            distribution[status] = distribution.get(status, 0) + 1

        return distribution

    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to risk level."""
        if score > 70:
            return "critical"
        if score > 50:
            return "high"
        if score > 25:
            return "medium"
        return "low"

    async def detect_circular_dependencies(self) -> list[list[str]]:
        """Find all circular dependency chains.

        Returns:
            List of cycles, each cycle is a list of item IDs
        """
        if not self.graph:
            msg = "Graph not built. Call build_graph() first."
            raise ValueError(msg)

        cycles = list(nx.simple_cycles(self.graph))
        logger.warning(f"Found {len(cycles)} circular dependencies")

        return cycles


# ============================================================================
# UNIFIED ENHANCEMENT SERVICE
# ============================================================================


@invariant(lambda self: self.semantic_service is not None)
@invariant(lambda self: self.quality_service is not None)
@invariant(lambda self: self.impact_service is not None)
class RequirementEnhancementService:
    """Master service orchestrating all enhancement capabilities.

    Provides unified interface for requirement analysis and improvement.
    """

    def __init__(self) -> None:
        """Initialize all enhancement services."""
        logger.info("Initializing Requirement Enhancement Service")

        self.semantic_service = SemanticAnalysisService()
        self.quality_service = QualityAnalysisService()
        self.impact_service = ImpactAnalysisService()

    @require(lambda item_id: isinstance(item_id, str) and len(item_id) > 0)
    @ensure(lambda result: result is not None)
    async def enhance_requirement(
        self,
        item_id: str,
        description: str,
        capabilities: list[EnhancementCapability] | None = None,
    ) -> dict[str, Any]:
        """Apply requested enhancements to a requirement.

        Args:
            item_id: Requirement ID
            description: Requirement description
            capabilities: List of capabilities to apply (default: all)

        Returns:
            Dict with enhancement results
        """
        if capabilities is None:
            capabilities = [
                EnhancementCapability.QUALITY_ANALYSIS,
                EnhancementCapability.SEMANTIC_ANALYSIS,
            ]

        results = {"item_id": item_id, "enhancements": {}, "timestamp": datetime.now().isoformat()}

        # Quality analysis
        if EnhancementCapability.QUALITY_ANALYSIS in capabilities:
            quality = await self.quality_service.analyze_requirement(description)
            results["enhancements"]["quality"] = asdict(quality)

        # Semantic analysis (requires other requirements for comparison)
        if EnhancementCapability.SEMANTIC_ANALYSIS in capabilities:
            results["enhancements"]["semantic"] = {
                "capability": "semantic_analysis",
                "status": "requires_other_requirements_for_comparison",
            }

        return results

    @require(lambda requirements: isinstance(requirements, list))
    async def find_duplicates(
        self,
        requirements: list[dict[str, str]],
        threshold: float = 0.85,
    ) -> list[DuplicateCandidate]:
        """Find duplicate requirements across a set.

        Args:
            requirements: List of requirement dicts
            threshold: Similarity threshold

        Returns:
            List of DuplicateCandidate objects
        """
        return await self.semantic_service.find_duplicate_requirements(requirements, threshold)

    @require(lambda items: isinstance(items, list))
    @require(lambda links: isinstance(links, list))
    async def analyze_impact(
        self,
        item_id: str,
        items: list[dict[str, Any]],
        links: list[dict[str, Any]],
    ) -> ImpactAnalysis:
        """Analyze impact of changing a requirement.

        Args:
            item_id: Target item ID
            items: All items in project
            links: All links in project

        Returns:
            ImpactAnalysis results
        """
        await self.impact_service.build_graph(items, links)
        return await self.impact_service.calculate_impact(item_id)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


async def example_basic_quality_analysis() -> None:
    """Example: Analyze requirement quality."""
    service = RequirementEnhancementService()

    requirement = "The system should be fast and reliable"

    return await service.enhance_requirement(item_id="REQ-001", description=requirement)


async def example_duplicate_detection() -> None:
    """Example: Find duplicate requirements."""
    service = RequirementEnhancementService()

    requirements = [
        {
            "id": "REQ-001",
            "title": "User authentication",
            "description": "The system shall authenticate users using OAuth 2.0",
        },
        {
            "id": "REQ-002",
            "title": "OAuth authentication",
            "description": "The system should support OAuth 2.0 for user authentication",
        },
        {
            "id": "REQ-003",
            "title": "Password policy",
            "description": "The system shall enforce strong password requirements",
        },
    ]

    duplicates = await service.find_duplicates(requirements, threshold=0.80)

    for _dup in duplicates:
        pass

    return duplicates


async def example_impact_analysis() -> None:
    """Example: Analyze impact of requirement change."""
    service = RequirementEnhancementService()

    items = [
        {"id": "REQ-001", "title": "Authentication", "status": "done", "priority": 1},
        {"id": "REQ-002", "title": "OAuth support", "status": "done", "priority": 1},
        {"id": "REQ-003", "title": "Password policy", "status": "testing", "priority": 2},
        {"id": "REQ-004", "title": "Login UI", "status": "draft", "priority": 2},
    ]

    links = [
        {"source_id": "REQ-001", "target_id": "REQ-002", "link_type": "depends_on"},
        {"source_id": "REQ-002", "target_id": "REQ-003", "link_type": "depends_on"},
        {"source_id": "REQ-001", "target_id": "REQ-004", "link_type": "depends_on"},
    ]

    return await service.analyze_impact("REQ-001", items, links)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    asyncio.run(example_basic_quality_analysis())

    asyncio.run(example_duplicate_detection())

    asyncio.run(example_impact_analysis())
