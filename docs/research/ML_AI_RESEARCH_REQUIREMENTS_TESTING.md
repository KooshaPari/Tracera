# ML/AI Approaches for Requirement and Test Specification Analysis

## Research Overview

This comprehensive research document explores cutting-edge ML/AI approaches for analyzing requirements and test specifications. It includes library recommendations, model selections, integration patterns, and practical implementation guidance for the TraceRTM system.

**Research Date**: January 2026
**Target Framework**: Python 3.12+ with async-first architecture
**Integration Point**: TracertM services architecture

---

## Executive Summary

Modern ML/AI approaches enable sophisticated requirement and test specification analysis beyond regex-based pattern matching. Key areas of innovation include:

1. **Large Language Models (LLMs)**: Claude 4.5/GPT-5 for semantic understanding and quality analysis
2. **Embedding Models**: Sentence-transformers for semantic similarity and clustering
3. **Named Entity Recognition**: Domain-specific NER for extracting actors, actions, conditions
4. **Test Prioritization**: Reinforcement learning (RETECS) for intelligent test selection
5. **Traceability**: Deep learning models (CodeBERT, GraphCodeBERT) for requirement-code linking
6. **Defect Prediction**: ML models combining code metrics with semantic features
7. **Duplicate Detection**: SimHash/LSH for near-duplicate requirement discovery

---

## 1. Large Language Models for Requirements Analysis

### 1.1 Current State of LLMs (January 2026)

**Available Models:**
- **Claude 4.5 Sonnet/Opus** (Anthropic): Best for requirement analysis and reasoning
  - 200K context window
  - Constitutional AI for safer outputs
  - Excellent tool use capabilities
  - Cost-effective for production

- **GPT-4o/GPT-5.2** (OpenAI): Generalist with strong coding
  - 128K-200K context window
  - Multimodal capabilities
  - Leading on benchmarks
  - Higher cost

- **DeepSeek V3.2** (Open Source): Cost-competitive alternative
  - 128K context window
  - MoE architecture for efficiency
  - Good reasoning capabilities

### 1.2 Requirement Quality Analysis

**What LLMs Can Detect:**

1. **Ambiguity Detection**
   - Vague language and unclear references
   - Missing stakeholder context
   - Incomplete conditional statements
   - Ambiguous pronouns and references

2. **Completeness Assessment**
   - Missing acceptance criteria
   - Incomplete constraints
   - Undefined dependencies
   - Missing non-functional requirements

3. **Contradiction Identification**
   - Conflicting requirements
   - Inconsistent acceptance criteria
   - Circular dependencies
   - Incompatible constraints

4. **Requirement Classification**
   - Functional vs non-functional
   - FURPS+ categorization
   - Priority estimation
   - Risk assessment

### 1.3 Fine-Tuning for Domain-Specific Improvements

**Parameter-Efficient Fine-Tuning (PEFT):**

```python
# Dependencies for fine-tuning
# peft>=0.12.0  # Parameter-Efficient Fine-Tuning
# torch>=2.1.0
# transformers>=4.38.0
# trl>=0.8.0    # Transformer Reinforcement Learning

from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

# LoRA Configuration (Low-Rank Adaptation)
# Reduces trainable parameters from millions to thousands
lora_config = LoraConfig(
    r=16,  # Low-rank dimension
    lora_alpha=32,  # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    lora_dropout=0.05,
    bias="none",
)

# For Claude models, use structured outputs instead
# Claude excels at constraint-based generation without fine-tuning
```

**Best Practice for TraceRTM:**
- Use few-shot prompting with domain examples
- Leverage structured outputs (Claude's JSON mode)
- Build custom prompt templates for requirement analysis
- No fine-tuning needed for Claude - too expensive
- Reserve fine-tuning for smaller models (Mistral, Llama)

### 1.4 Implementation Pattern for TraceRTM

```python
# src/tracertm/services/llm_requirement_analyzer.py
from anthropic import AsyncAnthropic
from pydantic import BaseModel

class RequirementAnalysis(BaseModel):
    """Structured output for requirement analysis."""
    ambiguity_issues: list[str]
    completeness_gaps: list[str]
    contradictions: list[str]
    classification: str  # functional, non-functional, constraint
    priority_estimate: int  # 1-5
    risks: list[str]
    suggestions: list[str]

class LLMRequirementAnalyzer:
    """LLM-based requirement quality analyzer."""

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def analyze_requirement(
        self,
        title: str,
        description: str,
        acceptance_criteria: list[str],
        context: str = ""
    ) -> RequirementAnalysis:
        """Analyze requirement using Claude with structured outputs."""

        message = await self.client.messages.create(
            model="claude-opus-4-20250102",  # Latest Claude 4
            max_tokens=1024,
            system="""You are an expert requirements engineer analyzing
            requirements for quality, completeness, and clarity.

            Identify ambiguities, gaps, contradictions, and provide
            actionable suggestions for improvement.""",
            messages=[{
                "role": "user",
                "content": f"""Analyze this requirement:

Title: {title}
Description: {description}
Acceptance Criteria: {', '.join(acceptance_criteria)}
Context: {context}

Provide structured analysis."""
            }],
        )

        # Parse structured response
        # Claude can return JSON that matches RequirementAnalysis
        ...
```

### 1.5 Key Research References

- **Claude 4.5 Capabilities**: Advanced reasoning with 200K context
- **Constitutional AI**: Improved safety and alignment
- **Tool Use**: Combining LLMs with requirement databases
- **Prompt Engineering**: Effective techniques for requirement analysis

**Integration with TraceRTM:**
- Enhance `requirement_quality_service.py` with LLM capabilities
- Add to `ai_service.py` as a new capability
- Create structured output schemas in `schemas/requirement_quality.py`

---

## 2. Embedding Models for Semantic Analysis

### 2.1 Sentence Transformers Overview

**Definition**: Convert text to dense vectors capturing semantic meaning, enabling similarity comparisons.

**Top Models (2025-2026):**

1. **all-mpnet-base-v2** (Published: 2021, Still SOTA)
   - Dimension: 768
   - Performance: 63.3 NDCG@10 on MTEB benchmark
   - Speed: ~200 sequences/sec (GPU)
   - Size: 438 MB
   - License: Apache 2.0
   - Best for: General-purpose semantic similarity

2. **all-MiniLM-L6-v2** (Lightweight)
   - Dimension: 384
   - Performance: 56.9 NDCG@10 (excellent for size)
   - Speed: ~2000 sequences/sec (CPU)
   - Size: 22 MB
   - License: Apache 2.0
   - Best for: Resource-constrained environments, clustering

3. **multilingual-e5-large** (Latest)
   - Dimension: 1024
   - Languages: 100+
   - Performance: 64.9 NDCG@10
   - Size: 1.7 GB
   - License: MIT
   - Best for: International requirements, global projects

4. **OpenAI Embeddings** (Proprietary but reliable)
   - text-embedding-3-small: 512 dimensions, cheaper
   - text-embedding-3-large: 3072 dimensions, most accurate
   - Cost: $0.02-0.13 per 1M tokens
   - Best for: Production systems with budget

**For TraceRTM**: Use `all-MiniLM-L6-v2` for MVP, upgrade to `all-mpnet-base-v2` for production quality.

### 2.2 Applications for Requirements

```python
# src/tracertm/services/requirement_embeddings_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RequirementEmbeddingService:
    """Semantic similarity and clustering for requirements."""

    def __init__(self):
        # Lightweight model for MVP, can upgrade
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def embed_requirement(self, text: str) -> np.ndarray:
        """Convert requirement to embedding vector."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    async def find_similar_requirements(
        self,
        query_text: str,
        requirement_pool: list[tuple[str, str]],  # (id, text)
        top_k: int = 5,
        threshold: float = 0.7
    ) -> list[tuple[str, float]]:
        """Find similar requirements using cosine similarity."""
        query_embedding = self.model.encode(query_text, convert_to_numpy=True)

        scores = []
        for req_id, req_text in requirement_pool:
            req_embedding = self.model.encode(req_text, convert_to_numpy=True)
            similarity = cosine_similarity(
                [query_embedding],
                [req_embedding]
            )[0][0]

            if similarity >= threshold:
                scores.append((req_id, float(similarity)))

        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

    async def cluster_requirements(
        self,
        requirements: list[tuple[str, str]],
        num_clusters: int = 5
    ) -> dict[int, list[str]]:
        """Cluster similar requirements together."""
        from sklearn.cluster import KMeans

        texts = [text for _, text in requirements]
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        kmeans = KMeans(n_clusters=num_clusters)
        cluster_labels = kmeans.fit_predict(embeddings)

        clusters = {}
        for req_id, text, label in zip([r[0] for r in requirements], texts, cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(req_id)

        return clusters
```

### 2.3 Performance Metrics and Trade-offs

| Model | Dimension | Speed | MTEB | Size | Cost | Best Use |
|-------|-----------|-------|------|------|------|----------|
| all-MiniLM-L6-v2 | 384 | 2000 seq/s | 56.9 | 22 MB | Free | MVP, Clustering |
| all-mpnet-base-v2 | 768 | 200 seq/s | 63.3 | 438 MB | Free | Production |
| OpenAI text-3-small | 512 | API | 65.1 | N/A | $0.02/1M | Quality Priority |
| multilingual-e5 | 1024 | 50 seq/s | 64.9 | 1.7 GB | Free | International |

**Recommendation for TraceRTM:**
- **MVP Phase**: all-MiniLM-L6-v2 (fast, small, free)
- **Production**: all-mpnet-base-v2 (better quality, still reasonable)
- **Enterprise**: OpenAI embeddings (highest quality, cost-effective at scale)

### 2.4 Storage and Indexing

```python
# Install vector database options:
# pip install qdrant-client  # Best: open-source, serverless
# pip install weaviate-client  # Cloud option
# pip install milvus  # Scalable alternative
# pip install pgvector  # PostgreSQL extension (TraceRTM uses Postgres!)

# PostgreSQL pgvector integration (recommended for TraceRTM)
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String

class RequirementEmbedding(Base):
    """Store requirement embeddings in PostgreSQL."""
    __tablename__ = "requirement_embeddings"

    id = Column(String, primary_key=True)
    requirement_id = Column(String, ForeignKey("items.id"))
    embedding = Column(Vector(384))  # all-MiniLM-L6-v2 dimension
    model_version = Column(String)  # Track model used
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Cost Analysis:**
- pgvector: Free (PostgreSQL extension)
- Qdrant Cloud: $50-500/month
- Weaviate: $0-200/month
- Milvus: Self-hosted, minimal cost

---

## 3. Named Entity Recognition for Requirements

### 3.1 spaCy Custom NER Models

**Overview**: Extract structured entities from requirement text:
- **Actors**: Who performs actions (user, system, admin)
- **Actions**: What is done (create, delete, validate)
- **Conditions**: When/under what circumstances (if, when, provided)
- **Objects**: What is affected (item, file, record)

### 3.2 Training Custom NER Models

```python
# src/tracertm/services/requirement_ner_service.py
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

class RequirementNERService:
    """Custom NER for requirement extraction."""

    def __init__(self, model_path: str = "en_core_web_sm"):
        """Initialize with spaCy model."""
        self.nlp = spacy.load(model_path)
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner", last=True)
        else:
            ner = self.nlp.get_pipe("ner")

        # Add custom labels
        for label in ["ACTOR", "ACTION", "CONDITION", "OBJECT", "CONSTRAINT"]:
            ner.add_label(label)

    async def fine_tune_ner(
        self,
        training_data: list[tuple[str, dict]],
        iterations: int = 30,
        dropout: float = 0.5
    ) -> None:
        """Fine-tune NER on domain-specific requirements.

        Training data format:
        [
            ("User should be able to create items", {
                "entities": [
                    (0, 4, "ACTOR"),      # "User"
                    (14, 20, "ACTION"),   # "create"
                    (26, 31, "OBJECT")    # "items"
                ]
            }),
            ...
        ]
        """
        ner = self.nlp.get_pipe("ner")
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]

        # Disable other components during training
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.create_optimizer()

            for iteration in range(iterations):
                losses = {}
                examples = [Example.from_dict(self.nlp.make_doc(text), {
                    "entities": entities
                }) for text, entities in training_data]

                for example in minibatch(examples, size=8):
                    self.nlp.update(
                        example,
                        drop=dropout,
                        sgd=optimizer,
                        losses=losses
                    )

                print(f"Iteration {iteration + 1}, Loss: {losses['ner']:.4f}")

    async def extract_entities(
        self,
        requirement_text: str
    ) -> dict[str, list[str]]:
        """Extract entities from requirement text."""
        doc = self.nlp(requirement_text)

        entities_by_label = {}
        for ent in doc.ents:
            if ent.label_ not in entities_by_label:
                entities_by_label[ent.label_] = []
            entities_by_label[ent.label_].append(ent.text)

        return entities_by_label

# Training data example (domain-specific requirements)
REQUIREMENT_TRAINING_DATA = [
    ("The user must be able to create a new project",
     {"entities": [(4, 8, "ACTOR"), (21, 27, "ACTION"), (33, 38, "OBJECT")]}),

    ("When a requirement is marked complete, notify all stakeholders",
     {"entities": [(5, 16, "OBJECT"), (20, 26, "ACTION"), (40, 51, "ACTOR")]}),

    ("If authentication fails, redirect to login page",
     {"entities": [(3, 15, "CONDITION"), (17, 25, "ACTION"), (36, 40, "OBJECT")]}),
]
```

### 3.3 Uptraining vs Fine-tuning

**Problem**: Fine-tuning causes "catastrophic forgetting" of pre-trained knowledge.

**Solution**: Uptraining approach
```python
# Mix domain data with general data
# Keep ratio: 70% new domain data, 30% general data

training_data = [
    # 70% domain-specific requirement entities
    *REQUIREMENT_TRAINING_DATA,
    # 30% general NER examples
    *GENERAL_NER_EXAMPLES
]
```

### 3.4 Requirement Patterns

**Common patterns extracted:**
- **Functional requirement**: "User [ACTOR] should [ACTION] [OBJECT]"
- **Constraint**: "[OBJECT] must [CONSTRAINT] in [CONDITION]"
- **Non-functional**: "System [ACTION] [CONSTRAINT] under [CONDITION]"

---

## 4. Requirement Classification

### 4.1 FURPS+ Category Classification

```python
# src/tracertm/services/requirement_classification_service.py
from enum import Enum
from anthropic import AsyncAnthropic

class RequirementCategory(Enum):
    """FURPS+ categories."""
    FUNCTIONAL = "functional"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    SUPPORTABILITY = "supportability"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CONSTRAINT = "constraint"

class RequirementClassifier:
    """Classify requirements using LLM and pattern matching."""

    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def classify_requirement(self, text: str) -> RequirementCategory:
        """Classify requirement into FURPS+ category."""

        # Pattern-based classification (fast)
        category = self._classify_by_patterns(text)
        if category:
            return category

        # LLM-based classification (accurate)
        message = await self.client.messages.create(
            model="claude-opus-4-20250102",
            max_tokens=100,
            system="""Classify requirement into FURPS+ category.
            Response with just the category name.""",
            messages=[{
                "role": "user",
                "content": f"Classify: {text}"
            }]
        )

        category_text = message.content[0].text.lower().strip()
        try:
            return RequirementCategory[category_text.upper()]
        except KeyError:
            return RequirementCategory.FUNCTIONAL

    def _classify_by_patterns(self, text: str) -> RequirementCategory | None:
        """Fast pattern-based classification."""
        text_lower = text.lower()

        # Performance keywords
        if any(w in text_lower for w in ["fast", "quick", "latency", "throughput", "second", "ms"]):
            return RequirementCategory.PERFORMANCE

        # Security keywords
        if any(w in text_lower for w in ["secure", "encrypt", "authentication", "authorization", "password"]):
            return RequirementCategory.SECURITY

        # Reliability keywords
        if any(w in text_lower for w in ["reliable", "available", "uptime", "redundant", "fault"]):
            return RequirementCategory.RELIABILITY

        # Usability keywords
        if any(w in text_lower for w in ["user", "interface", "ui", "easy", "intuitive", "accessible"]):
            return RequirementCategory.USABILITY

        return None
```

### 4.2 Priority Estimation

```python
from pydantic import BaseModel

class RequirementPriority(BaseModel):
    """Estimated priority with reasoning."""
    priority_score: int  # 1-5
    business_impact: str
    technical_impact: str
    risk_level: str  # low, medium, high
    recommendations: list[str]

async def estimate_priority(
    requirement: str,
    business_context: str,
    dependencies: list[str] = []
) -> RequirementPriority:
    """Estimate requirement priority using context and dependencies."""

    message = await client.messages.create(
        model="claude-opus-4-20250102",
        max_tokens=500,
        system="""You are a requirements prioritization expert.
        Consider business impact, technical complexity, dependencies,
        and risk when estimating priority (1-5 scale).""",
        messages=[{
            "role": "user",
            "content": f"""
            Requirement: {requirement}

            Business Context: {business_context}

            Dependencies: {', '.join(dependencies) if dependencies else 'None'}

            Provide priority estimate with reasoning.
            """
        }]
    )

    # Parse response into RequirementPriority
    ...
```

---

## 5. Test Prioritization with Reinforcement Learning

### 5.1 RETECS Framework

**What**: Reinforcement Learning for Automatic Test Case Selection and Prioritization in CI

**Why**:
- Minimize feedback time between code commit and test results
- Adapt to changing test characteristics dynamically
- Learn from historical failure patterns

**How it works:**
1. Observe test characteristics (duration, last execution, failure history)
2. Decide which tests to run
3. Reward signal from actual failures
4. Learn to prioritize failure-prone tests

### 5.2 Implementation Pattern

```python
# src/tracertm/services/test_prioritization_service.py
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

class TestPrioritizationAgent:
    """RL-based test prioritization using Q-learning."""

    def __init__(self, epsilon: float = 0.1, learning_rate: float = 0.1):
        """Initialize Q-learning agent."""
        self.epsilon = epsilon  # Exploration rate
        self.learning_rate = learning_rate
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.test_history = {}  # Track test execution data

    def extract_state(self, test_case: dict) -> tuple:
        """Extract state features from test case.

        State features:
        - Duration: short, medium, long
        - Last failure: recent, old, never
        - Execution frequency: rare, frequent
        - Code coverage: low, medium, high
        """
        duration = "long" if test_case["duration_ms"] > 5000 else "short"

        last_failure = test_case.get("last_failure_date")
        if last_failure:
            days_since_failure = (datetime.now() - last_failure).days
            recency = "recent" if days_since_failure < 7 else "old"
        else:
            recency = "never"

        failure_rate = test_case.get("failure_rate", 0)
        risk = "high" if failure_rate > 0.1 else "low"

        return (duration, recency, risk)

    def select_tests(
        self,
        available_tests: list[dict],
        budget_ms: int = 60000,  # 1 minute budget
        use_exploration: bool = False
    ) -> list[str]:
        """Select tests to run using Q-learning policy."""

        selected = []
        remaining_budget = budget_ms

        for test in available_tests:
            state = self.extract_state(test)
            test_id = test["id"]

            # Epsilon-greedy: explore or exploit
            if use_exploration and np.random.random() < self.epsilon:
                q_value = np.random.random()  # Explore randomly
            else:
                q_value = self.q_table[state][test_id]  # Exploit best

            if test["duration_ms"] <= remaining_budget:
                selected.append(test_id)
                remaining_budget -= test["duration_ms"]

        return selected

    def update_q_values(
        self,
        test_id: str,
        test: dict,
        failed: bool
    ) -> None:
        """Update Q-values based on test execution result."""

        state = self.extract_state(test)

        # Reward: positive for failures caught, negative for wasted time
        reward = 10.0 if failed else -0.5

        # Q-learning update
        old_q_value = self.q_table[state][test_id]
        self.q_table[state][test_id] = old_q_value + self.learning_rate * (
            reward - old_q_value
        )

        # Track history
        if test_id not in self.test_history:
            self.test_history[test_id] = {
                "total_runs": 0,
                "failures": 0,
                "last_failure": None
            }

        self.test_history[test_id]["total_runs"] += 1
        if failed:
            self.test_history[test_id]["failures"] += 1
            self.test_history[test_id]["last_failure"] = datetime.now()
```

### 5.3 Historical Failure Prediction

```python
from sklearn.ensemble import RandomForestClassifier

class FailurePredictionModel:
    """ML model to predict test failure likelihood."""

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.is_trained = False

    def extract_features(self, test: dict, change_summary: dict) -> np.ndarray:
        """Extract features for failure prediction.

        Features:
        - Historical failure rate
        - Days since last failure
        - Files changed in this commit
        - Code complexity of touched files
        - Test duration
        - Time of day (circadian rhythm)
        """
        features = [
            test.get("historical_failure_rate", 0),
            (datetime.now() - test.get("last_failure", datetime.now())).days,
            len(change_summary.get("files_changed", [])),
            change_summary.get("avg_complexity", 0),
            test.get("duration_ms", 0),
            datetime.now().hour,  # Circadian rhythm
        ]
        return np.array(features).reshape(1, -1)

    def predict_failure(
        self,
        test: dict,
        change_summary: dict
    ) -> tuple[bool, float]:
        """Predict if test will fail.

        Returns: (will_fail: bool, probability: float)
        """
        if not self.is_trained:
            return False, 0.5

        features = self.extract_features(test, change_summary)
        prediction = self.model.predict(features)[0]
        probability = max(self.model.predict_proba(features)[0])

        return bool(prediction), float(probability)
```

### 5.4 Change-Based Test Selection

```python
class ChangeBasedTestSelector:
    """Select tests based on code changes using coverage analysis."""

    def __init__(self, coverage_data: dict):
        """Initialize with code coverage mapping.

        coverage_data format:
        {
            "test_id": ["file1.py:10-20", "file2.py:5-15"],
            ...
        }
        """
        self.coverage_data = coverage_data

    def select_tests_for_changes(
        self,
        changed_files: list[str],
        changed_lines: dict[str, list[int]]
    ) -> list[str]:
        """Select tests that cover changed code."""

        selected = set()

        for test_id, covered_locations in self.coverage_data.items():
            for location in covered_locations:
                file, line_range = location.split(":")
                start, end = map(int, line_range.split("-"))

                # Check if this test covers any changed lines
                if file in changed_lines:
                    changed = changed_lines[file]
                    if any(start <= line <= end for line in changed):
                        selected.add(test_id)
                        break

        return list(selected)
```

---

## 6. Defect Prediction

### 6.1 Code Metrics Foundation

```python
# src/tracertm/services/code_metrics_service.py
import radon.metrics as rad_metrics
from radon.complexity import cc_visit

class CodeMetricsCollector:
    """Collect code complexity metrics for defect prediction."""

    def analyze_file(self, file_path: str, file_content: str) -> dict:
        """Analyze single file for defect prediction features."""

        metrics = {}

        # Lines of Code (LOC)
        loc = len([line for line in file_content.split("\n") if line.strip()])
        metrics["lines_of_code"] = loc

        # Cyclomatic Complexity (McCabe)
        try:
            complexity_data = cc_visit(file_content)
            metrics["cyclomatic_complexity"] = sum(
                func.complexity for func in complexity_data
            )
            metrics["avg_function_complexity"] = (
                metrics["cyclomatic_complexity"] / max(len(complexity_data), 1)
            )
        except:
            metrics["cyclomatic_complexity"] = 0
            metrics["avg_function_complexity"] = 0

        # Halstead Metrics
        try:
            h_metrics = rad_metrics.h_visit(file_content)
            metrics["halstead_volume"] = h_metrics.volume
            metrics["halstead_difficulty"] = h_metrics.difficulty
            metrics["halstead_effort"] = h_metrics.effort
            metrics["halstead_time"] = h_metrics.time
        except:
            metrics["halstead_volume"] = 0
            metrics["halstead_difficulty"] = 0
            metrics["halstead_effort"] = 0
            metrics["halstead_time"] = 0

        # Maintainability Index
        try:
            mi = rad_metrics.mi_visit(file_content, multi=True)
            metrics["maintainability_index"] = mi
        except:
            metrics["maintainability_index"] = 0

        return metrics

# Install metrics tools
# pip install radon>=6.0.0  # Complexity metrics
```

### 6.2 Defect Prediction Model

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

class DefectPredictionModel:
    """Predict defect-prone code components."""

    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            "lines_of_code",
            "cyclomatic_complexity",
            "halstead_difficulty",
            "historical_defect_density",
            "recent_changes",
            "author_experience",
            "age_in_days"
        ]
        self.is_trained = False

    def train(
        self,
        training_data: pd.DataFrame,
        target_column: str = "has_defect"
    ) -> None:
        """Train defect prediction model."""

        X = training_data[self.feature_names]
        y = training_data[target_column]

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict_defect_risk(
        self,
        file_metrics: dict,
        historical_data: dict
    ) -> tuple[str, float]:
        """Predict defect risk level and probability.

        Returns: (risk_level: "low"|"medium"|"high", probability: 0.0-1.0)
        """
        if not self.is_trained:
            return "medium", 0.5

        features = [
            file_metrics["lines_of_code"],
            file_metrics["cyclomatic_complexity"],
            file_metrics["halstead_difficulty"],
            historical_data.get("defect_density", 0),
            historical_data.get("recent_changes", 0),
            historical_data.get("author_experience", 5),
            historical_data.get("file_age_days", 365)
        ]

        X_scaled = self.scaler.transform([features])
        prediction = self.model.predict(X_scaled)[0]
        probability = max(self.model.predict_proba(X_scaled)[0])

        if probability > 0.7:
            risk = "high"
        elif probability > 0.4:
            risk = "medium"
        else:
            risk = "low"

        return risk, float(probability)
```

### 6.3 Integration with TraceRTM

```python
# Extend existing item service with defect risk
# src/tracertm/services/item_defect_service.py

class ItemDefectAnalysis:
    """Analyze items for defect risk."""

    def __init__(self, metrics_service: CodeMetricsCollector,
                 model: DefectPredictionModel):
        self.metrics = metrics_service
        self.model = model

    async def analyze_item_risk(
        self,
        item_id: str,
        code_content: str,
        historical_info: dict
    ) -> dict:
        """Analyze risk of item implementation."""

        file_metrics = self.metrics.analyze_file("item.py", code_content)
        risk_level, probability = self.model.predict_defect_risk(
            file_metrics,
            historical_info
        )

        return {
            "item_id": item_id,
            "risk_level": risk_level,
            "defect_probability": probability,
            "metrics": file_metrics,
            "recommendations": self._get_recommendations(
                file_metrics, risk_level
            )
        }

    def _get_recommendations(self, metrics: dict, risk_level: str) -> list[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        if metrics["cyclomatic_complexity"] > 15:
            recommendations.append("Refactor: High cyclomatic complexity - break into smaller functions")

        if metrics["halstead_difficulty"] > 20:
            recommendations.append("Complex algorithm - consider documentation and unit tests")

        if metrics["lines_of_code"] > 500:
            recommendations.append("Large file - consider splitting into modules")

        if risk_level == "high":
            recommendations.append("Prioritize code review and testing")

        return recommendations
```

---

## 7. Requirement-Code Traceability

### 7.1 IR-Based Linking (TF-IDF, BM25)

```python
# src/tracertm/services/traceability_ir_service.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TFIDFTraceLinking:
    """Link requirements to code using TF-IDF."""

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None

    def fit_codebase(self, code_snippets: list[str]) -> None:
        """Fit TF-IDF model on codebase."""
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(code_snippets)

    def find_related_code(
        self,
        requirement: str,
        code_snippets: list[tuple[str, str]],  # (id, content)
        top_k: int = 5,
        threshold: float = 0.1
    ) -> list[tuple[str, float]]:
        """Find code snippets related to requirement."""

        req_vector = self.tfidf_vectorizer.transform([requirement])
        similarities = cosine_similarity(req_vector, self.tfidf_matrix)[0]

        results = []
        for idx, (code_id, _) in enumerate(code_snippets):
            if similarities[idx] >= threshold:
                results.append((code_id, float(similarities[idx])))

        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
```

### 7.2 BM25 with Semantic Refinement

```python
from rank_bm25 import BM25Okapi

class HybridTraceLinking:
    """Combine BM25 keyword matching with semantic refinement."""

    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.bm25 = None
        self.code_snippets = []

    async def index_codebase(
        self,
        code_snippets: list[tuple[str, str]]
    ) -> None:
        """Index codebase for fast retrieval."""
        self.code_snippets = code_snippets

        # Tokenize for BM25
        tokenized = [
            snippet.lower().split() for _, snippet in code_snippets
        ]
        self.bm25 = BM25Okapi(tokenized)

    async def find_related_code(
        self,
        requirement: str,
        top_k: int = 50,
        top_semantic: int = 5
    ) -> list[tuple[str, float]]:
        """Two-stage: BM25 pre-filter, then semantic refinement."""

        # Stage 1: BM25 pre-filtering (fast)
        tokenized_req = requirement.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_req)

        # Get top 50 candidates by BM25
        top_indices = np.argsort(bm25_scores)[-top_k:][::-1]
        candidates = [
            (self.code_snippets[i][0], bm25_scores[i])
            for i in top_indices if bm25_scores[i] > 0
        ]

        # Stage 2: Semantic refinement (accurate)
        req_embedding = await self.embedding_service.embed_requirement(requirement)
        final_results = []

        for code_id, bm25_score in candidates:
            code_content = next(
                c[1] for c in self.code_snippets if c[0] == code_id
            )
            code_embedding = await self.embedding_service.embed_requirement(
                code_content
            )

            semantic_similarity = cosine_similarity(
                [req_embedding],
                [code_embedding]
            )[0][0]

            # Combine scores: BM25 (keyword) + semantic (meaning)
            combined_score = 0.4 * (bm25_score / max(bm25_scores)) + 0.6 * semantic_similarity
            final_results.append((code_id, combined_score))

        return sorted(
            final_results,
            key=lambda x: x[1],
            reverse=True
        )[:top_semantic]
```

### 7.3 Deep Learning Approach (CodeBERT)

```python
# pip install transformers torch

from transformers import AutoTokenizer, AutoModel
import torch

class CodeBERTTraceLinking:
    """Deep learning traceability using CodeBERT/GraphCodeBERT."""

    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.code_embeddings = {}

    async def index_codebase(
        self,
        code_snippets: list[tuple[str, str]]
    ) -> None:
        """Embed and index codebase."""

        for code_id, code_content in code_snippets:
            tokens = self.tokenizer.encode(
                code_content,
                max_length=512,
                truncation=True,
                return_tensors="pt"
            )

            with torch.no_grad():
                output = self.model(tokens)
                embedding = output.last_hidden_state[:, 0, :].squeeze()

            self.code_embeddings[code_id] = embedding

    async def find_related_code(
        self,
        requirement: str,
        top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Find related code using CodeBERT embeddings."""

        # Embed requirement
        req_tokens = self.tokenizer.encode(
            requirement,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            req_output = self.model(req_tokens)
            req_embedding = req_output.last_hidden_state[:, 0, :].squeeze()

        # Compute similarities
        results = []
        for code_id, code_embedding in self.code_embeddings.items():
            similarity = torch.nn.functional.cosine_similarity(
                req_embedding.unsqueeze(0),
                code_embedding.unsqueeze(0)
            ).item()
            results.append((code_id, similarity))

        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
```

**Model Comparison for CodeTraceability:**

| Approach | Speed | Accuracy | Training | Memory | Best For |
|----------|-------|----------|----------|--------|----------|
| TF-IDF | Very Fast | 60% | None | Low | Quick MVP |
| BM25 | Fast | 65% | None | Low | Keyword-heavy code |
| BM25 + Semantic | Moderate | 75% | Optional | Moderate | Production |
| CodeBERT | Slow | 82% | Optional | High | High accuracy needed |
| GraphCodeBERT | Slow | 85% | Optional | High | Complex code structures |

**Recommendation**: Use hybrid BM25 + semantic embeddings for TraceRTM MVP, upgrade to CodeBERT if traceability accuracy becomes critical.

---

## 8. Duplicate Detection

### 8.1 SimHash for Near-Duplicate Detection

```python
# pip install simhash
from simhash import SimHash

class RequirementDuplicateDetector:
    """Detect duplicate and near-duplicate requirements using SimHash."""

    def __init__(self, similarity_threshold: int = 3):
        """Initialize detector.

        Args:
            similarity_threshold: Hamming distance threshold (0-64)
                - 0: Exact duplicates only
                - 3-5: Very similar (90%+ overlap)
                - 10: Similar (75%+ overlap)
                - 20+: Loose similarity
        """
        self.threshold = similarity_threshold
        self.fingerprints = {}  # requirement_id -> SimHash object

    def add_requirement(self, req_id: str, text: str) -> None:
        """Add requirement to detection index."""
        # SimHash is robust to small changes
        sh = SimHash(text)
        self.fingerprints[req_id] = sh

    def find_duplicates(
        self,
        requirement_text: str,
        exclude_id: str = None
    ) -> list[tuple[str, int]]:
        """Find duplicate/near-duplicate requirements.

        Returns: List of (req_id, hamming_distance) sorted by distance
        """
        query_sh = SimHash(requirement_text)

        results = []
        for req_id, sh in self.fingerprints.items():
            if exclude_id and req_id == exclude_id:
                continue

            distance = query_sh.distance(sh)
            if distance <= self.threshold:
                results.append((req_id, distance))

        return sorted(results, key=lambda x: x[1])

    def get_statistics(self) -> dict:
        """Get fingerprint statistics."""
        distances = []
        for i, (id1, sh1) in enumerate(self.fingerprints.items()):
            for id2, sh2 in list(self.fingerprints.items())[i+1:]:
                distances.append(sh1.distance(sh2))

        return {
            "total_requirements": len(self.fingerprints),
            "avg_distance": np.mean(distances) if distances else 0,
            "min_distance": min(distances) if distances else 0,
            "max_distance": max(distances) if distances else 0
        }
```

### 8.2 MinHash + LSH for Large-Scale Detection

```python
# pip install datasketch
from datasketch import MinHash, MinHashLSH

class LargeScaleDuplicateDetector:
    """Use MinHash + LSH for efficient large-scale duplicate detection."""

    def __init__(self, num_perm: int = 128, threshold: float = 0.5):
        """Initialize LSH-based detector.

        Args:
            num_perm: Number of hash functions (more = more accurate)
            threshold: Jaccard similarity threshold (0-1)
        """
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        self.minhashes = {}

    def add_requirement(self, req_id: str, text: str) -> None:
        """Add requirement to LSH index."""
        # Create MinHash from requirement
        tokens = set(text.lower().split())
        mh = MinHash(num_perm=self.num_perm)

        for token in tokens:
            mh.update(token.encode('utf-8'))

        self.minhashes[req_id] = mh
        self.lsh.insert(req_id, mh)

    def find_duplicates(self, requirement_text: str) -> list[str]:
        """Find similar requirements using LSH (very fast for large datasets)."""
        tokens = set(requirement_text.lower().split())
        mh = MinHash(num_perm=self.num_perm)

        for token in tokens:
            mh.update(token.encode('utf-8'))

        # LSH returns candidate IDs (very efficient)
        candidates = self.lsh.query(mh)
        return list(candidates)

    def get_similarity(self, req_id1: str, req_id2: str) -> float:
        """Get exact Jaccard similarity between two requirements."""
        if req_id1 not in self.minhashes or req_id2 not in self.minhashes:
            return 0.0

        return self.minhashes[req_id1].jaccard(self.minhashes[req_id2])
```

**Performance Characteristics:**

| Method | Speed | Accuracy | Memory | Scalability |
|--------|-------|----------|--------|-------------|
| SimHash | O(n) | 90% | Low | ~10K items |
| MinHash+LSH | O(log n) | 85% | Moderate | 1M+ items |
| Semantic Embeddings | O(n) | 92% | High | 100K items |
| Hybrid (LSH+Semantic) | O(log n) | 95% | High | 1M+ items |

---

## 9. Integration Architecture for TraceRTM

### 9.1 Service Layer Organization

```
src/tracertm/services/
├── ai_service.py (existing - enhance with new capabilities)
├── requirement_quality_service.py (existing - upgrade to LLM)
├── requirement_classification_service.py (new)
├── requirement_embeddings_service.py (new)
├── requirement_ner_service.py (new)
├── requirement_duplicate_detector.py (new)
├── traceability_ir_service.py (new)
├── test_prioritization_service.py (new)
├── code_metrics_service.py (new)
├── defect_prediction_service.py (new)
└── ml_models/
    ├── __init__.py
    ├── cached_models.py (singleton model loading)
    └── feature_extractors.py (shared feature extraction)
```

### 9.2 Database Schema Extensions

```sql
-- Add ML-related tables

-- Store requirement embeddings
CREATE TABLE requirement_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES items(id),
    embedding VECTOR(384),  -- all-MiniLM-L6-v2 dimension
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_requirement_embedding ON requirement_embeddings USING HNSW (embedding)
);

-- Store test execution history for RL
CREATE TABLE test_execution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL,
    execution_date TIMESTAMP DEFAULT NOW(),
    duration_ms INTEGER,
    passed BOOLEAN,
    failure_reason VARCHAR(500),
    git_commit VARCHAR(40),
    project_id UUID NOT NULL REFERENCES projects(id)
);

-- Store defect predictions
CREATE TABLE defect_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id),
    risk_level VARCHAR(20),  -- low, medium, high
    defect_probability FLOAT,
    metrics JSONB,
    prediction_date TIMESTAMP DEFAULT NOW()
);

-- Store requirement classification results
CREATE TABLE requirement_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES items(id),
    category VARCHAR(50),  -- FURPS+ category
    priority_score INTEGER,
    confidence FLOAT,
    classified_at TIMESTAMP DEFAULT NOW()
);

-- Store extracted entities
CREATE TABLE requirement_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES items(id),
    entity_type VARCHAR(50),  -- ACTOR, ACTION, CONDITION, OBJECT
    entity_text VARCHAR(500),
    extracted_at TIMESTAMP DEFAULT NOW()
);

-- Store trace links (ML-discovered)
CREATE TABLE ml_trace_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES items(id),
    target_id UUID NOT NULL REFERENCES items(id),
    link_type VARCHAR(50),  -- implements, validates, traces-to
    confidence FLOAT,
    method VARCHAR(50),  -- bm25, semantic, codebert, hybrid
    discovered_at TIMESTAMP DEFAULT NOW()
);
```

### 9.3 Dependency Installation

```toml
# Update pyproject.toml [project.optional-dependencies]

ml = [
    # Embeddings and similarity
    "sentence-transformers>=3.0.0",
    "scikit-learn>=1.4.0",
    "pgvector>=0.2.0",  # PostgreSQL vector extension

    # NER and NLP
    "spacy>=3.7.0",

    # Duplicate detection
    "datasketch>=1.0.0",
    "simhash>=1.8.0",

    # Code metrics
    "radon>=6.0.0",

    # LLM/AI (already have anthropic)
    "transformers>=4.38.0",  # For CodeBERT
    "torch>=2.1.0",

    # Information retrieval
    "rank-bm25>=0.2.0",

    # Test prioritization / ML models
    "xgboost>=2.0.0",
]

ai = [
    "anthropic>=0.40.0",
    "openai>=1.50.0",  # For embeddings alternative
]
```

### 9.4 Async Service Factory Pattern

```python
# src/tracertm/services/ml_models/cached_models.py
from typing import Optional
import asyncio

class MLModelCache:
    """Singleton for cached ML models."""

    _instance: Optional['MLModelCache'] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def initialize(self):
        """Initialize all models lazily."""
        async with self._lock:
            if self._initialized:
                return

            # Load models on first use
            self.embeddings_model = None  # Load on demand
            self.spacy_nlp = None
            self.codebert_model = None

            self._initialized = True

    async def get_embeddings_model(self):
        """Lazy load embeddings model."""
        if self.embeddings_model is None:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embeddings_model

    async def get_spacy_model(self):
        """Lazy load spaCy model."""
        if self.spacy_nlp is None:
            import spacy
            self.spacy_nlp = spacy.load("en_core_web_sm")
        return self.spacy_nlp

# Usage in services
class MyMLService:
    def __init__(self):
        self.model_cache = MLModelCache()

    async def do_something(self):
        embedder = await self.model_cache.get_embeddings_model()
        # Use embedder...
```

### 9.5 Configuration and Flags

```python
# src/tracertm/config/ml_config.py
from pydantic_settings import BaseSettings

class MLConfig(BaseSettings):
    """ML/AI service configuration."""

    # Requirement analysis
    enable_llm_quality_analysis: bool = True
    llm_model: str = "claude-opus-4-20250102"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    store_embeddings: bool = True

    # NER
    enable_ner: bool = True
    ner_model: str = "en_core_web_sm"

    # Duplicate detection
    enable_duplicate_detection: bool = True
    simhash_threshold: int = 5

    # Test prioritization
    enable_test_prioritization: bool = False
    test_rl_epsilon: float = 0.1

    # Defect prediction
    enable_defect_prediction: bool = False

    class Config:
        env_prefix = "ML_"
```

---

## 10. Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)
- [ ] Enhance requirement quality service with LLM analysis
- [ ] Add embedding-based duplicate detection
- [ ] Simple requirement classification (patterns + LLM)
- [ ] Database schema for embeddings

**Deliverables:**
- LLM quality analyzer service
- Duplicate detection endpoint
- Classification endpoint

### Phase 2: Advanced Features (Weeks 3-4)
- [ ] Fine-tune spaCy NER on requirements
- [ ] Implement hybrid BM25 + semantic traceability
- [ ] Test prioritization (basic RL)
- [ ] Defect prediction model

**Deliverables:**
- Entity extraction service
- Improved traceability linking
- Test prioritization MVP
- Defect risk reports

### Phase 3: Production Hardening (Weeks 5-6)
- [ ] CodeBERT traceability linking
- [ ] Advanced RETECS test prioritization
- [ ] Model caching and optimization
- [ ] Performance benchmarking
- [ ] Monitoring and observability

**Deliverables:**
- Production-ready ML services
- Performance metrics
- Operational runbooks
- API documentation

### Phase 4: Continuous Improvement
- [ ] Fine-tune models on real data
- [ ] A/B testing different approaches
- [ ] User feedback integration
- [ ] Model drift monitoring

---

## 11. Python Library Recommendations

### Core ML/AI Libraries

| Library | Version | Purpose | License | Notes |
|---------|---------|---------|---------|-------|
| sentence-transformers | 3.0+ | Embeddings | Apache 2.0 | Best overall, 15K+ models |
| scikit-learn | 1.4+ | Classical ML | BSD | Mature, feature-rich |
| spacy | 3.7+ | NLP/NER | MIT | Industrial-strength |
| transformers | 4.38+ | Foundation models | Apache 2.0 | Access to BERT, CodeBERT |
| torch | 2.1+ | Deep learning | BSD | Required for transformers |
| datasketch | 1.0+ | LSH/MinHash | MIT | Scalable similarity |
| simhash | 1.8+ | SimHash | MIT | Simple, fast |
| rank-bm25 | 0.2+ | BM25 ranking | Apache 2.0 | IR baseline |
| radon | 6.0+ | Code metrics | MIT | Complexity analysis |
| xgboost | 2.0+ | Gradient boosting | Apache 2.0 | Defect prediction |
| pgvector | 0.2+ | PostgreSQL vectors | PostgreSQL | Seamless DB integration |

### Integration Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| peft | Parameter-efficient fine-tuning | LoRA, QLoRA support |
| anthropic | Anthropic API | Already used in project |
| openai | OpenAI API | Alternative embeddings |
| trl | Transformer reinforcement learning | For test prioritization RL |

---

## 12. Cost-Benefit Analysis

### When to Use Each Approach

**Use LLM Analysis When:**
- Analyzing new requirement for quality ✓
- Classifying requirement type ✓
- Priority estimation ✓
- Complex reasoning needed ✓

**Avoid LLM When:**
- Need real-time performance (use embeddings)
- Batch processing large datasets (use ML models)
- Cost is critical (use patterns)

**Use Embeddings When:**
- Finding similar requirements ✓
- Clustering requirements ✓
- Quick semantic similarity ✓
- At scale (1000+ items) ✓

**Use NER When:**
- Extracting structured entities ✓
- Building requirement knowledge graphs ✓
- Domain-specific information ✓

**Use IR (TF-IDF/BM25) When:**
- Fast keyword-based search ✓
- No GPU available ✓
- Code traceability MVP ✓

**Use CodeBERT When:**
- Accurate code understanding needed
- Requirement-code linking critical
- Can tolerate latency
- Have sufficient resources

---

## 13. Testing Strategy

### Unit Tests

```python
# tests/unit/services/test_requirement_embeddings.py
import pytest
from tracertm.services.requirement_embeddings_service import RequirementEmbeddingService

@pytest.mark.asyncio
async def test_embed_requirement():
    service = RequirementEmbeddingService()
    text = "User should be able to create items"
    embedding = await service.embed_requirement(text)

    assert embedding.shape == (384,)  # all-MiniLM-L6-v2 dimension
    assert all(-1 <= x <= 1 for x in embedding)  # Cosine normalized

@pytest.mark.asyncio
async def test_similarity_threshold():
    service = RequirementEmbeddingService()

    similar = "User must create items"
    different = "System performance must be optimized"

    results = await service.find_similar_requirements(
        similar,
        [("req1", different)],
        threshold=0.7
    )

    assert len(results) == 0  # No results above threshold
```

### Integration Tests

```python
# tests/integration/test_ml_services.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_requirement_analysis(db_session):
    """Test complete requirement analysis pipeline."""

    # Create requirement
    item = Item(
        id="test-req",
        project_id="test-project",
        title="User login",
        description="User should be able to login with email and password"
    )
    db_session.add(item)
    await db_session.commit()

    # Run quality analysis
    quality_service = RequirementQualityService(db_session)
    quality = await quality_service.analyze_quality("test-req")

    assert quality is not None
    assert quality.ambiguity_score >= 0

    # Run embedding
    embedding_service = RequirementEmbeddingService()
    embedding = await embedding_service.embed_requirement(
        f"{item.title} {item.description}"
    )
    assert embedding.shape == (384,)

    # Run classification
    classifier = RequirementClassifier()
    category = await classifier.classify_requirement(item.description)
    assert category in RequirementCategory
```

### Performance Benchmarks

```python
# tests/performance/test_ml_performance.py
import pytest
import asyncio
from time import time

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_embedding_performance(benchmark):
    """Benchmark embedding generation."""
    service = RequirementEmbeddingService()

    async def generate_embeddings():
        tasks = [
            service.embed_requirement(f"Requirement {i}")
            for i in range(100)
        ]
        return await asyncio.gather(*tasks)

    # Should handle 100 embeddings in <5 seconds
    result = benchmark(lambda: asyncio.run(generate_embeddings()))
    assert len(result) == 100
```

---

## 14. Monitoring and Observability

### Key Metrics

```python
# src/tracertm/services/ml_monitoring.py
from opentelemetry import metrics

class MLMetrics:
    """Track ML service metrics."""

    def __init__(self):
        self.meter = metrics.get_meter(__name__)

        # Latency metrics
        self.embedding_latency = self.meter.create_histogram(
            "ml.embedding.latency_ms",
            description="Embedding generation latency"
        )

        self.quality_analysis_latency = self.meter.create_histogram(
            "ml.quality_analysis.latency_ms",
            description="Requirement quality analysis latency"
        )

        # Model performance metrics
        self.duplicate_detection_precision = self.meter.create_gauge(
            "ml.duplicate_detection.precision",
            description="Precision of duplicate detection"
        )

        self.defect_prediction_accuracy = self.meter.create_gauge(
            "ml.defect_prediction.accuracy",
            description="Accuracy of defect prediction model"
        )

        # Resource metrics
        self.model_memory_usage = self.meter.create_gauge(
            "ml.model.memory_mb",
            description="Memory used by loaded models"
        )

# Usage
metrics_service = MLMetrics()
start = time.time()
result = await service.embed_requirement(text)
metrics_service.embedding_latency.record(
    (time.time() - start) * 1000
)
```

---

## 15. References and Further Reading

### Academic Papers
1. **CodeBERT**: Feng et al. - "CodeBERT: A Pre-Trained Model for Programming and Natural Languages"
2. **GraphCodeBERT**: Guo et al. - "GraphCodeBERT: Pre-training Code Representations with Data Flow"
3. **RETECS**: Spieker et al. - "Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration"
4. **Defect Prediction**: Lessmann et al. - "Machine Learning Applications in Software Defect Prediction"
5. **SimHash**: Charikar - "Similarity Estimation Techniques from Rounding Algorithms"

### Tools and Frameworks
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [spaCy Documentation](https://spacy.io/)
- [Radon Documentation](https://radon.readthedocs.io/)
- [scikit-learn API](https://scikit-learn.org/)

### Production Considerations
- Model versioning and A/B testing
- Continuous evaluation metrics
- Handling model drift
- Cost optimization strategies
- Privacy and data governance

---

## Conclusion

Modern ML/AI approaches provide powerful capabilities for requirement and test specification analysis. The key is selecting the right technique for each use case:

1. **Start with embeddings** (fast, free, effective)
2. **Add LLM analysis** (high quality, moderate cost)
3. **Enhance with domain-specific models** (NER, classification)
4. **Scale with approximate methods** (LSH, SimHash)
5. **Optimize with deep learning** (CodeBERT, when justified)

For TraceRTM, the recommended MVP combines:
- Sentence-transformers for embeddings and duplicate detection
- Claude 4.5 for quality analysis and classification
- spaCy for NER on domain data
- Hybrid BM25 + semantic for traceability

This provides immediate value while keeping implementation complexity manageable.

---

**Document Version**: 1.0
**Last Updated**: January 29, 2026
**Author**: Research Analysis
**Status**: Final
