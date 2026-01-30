# ML/AI Integration Guide for TraceRTM

## Step-by-Step Implementation

### Step 1: Update Dependencies

**File**: `pyproject.toml`

```toml
[project.optional-dependencies]
ml = [
    # Embeddings and similarity
    "sentence-transformers>=3.0.0",
    "scikit-learn>=1.4.0",
    "pgvector>=0.2.0",

    # NER and NLP
    "spacy>=3.7.0",

    # Duplicate detection
    "datasketch>=1.0.0",
    "simhash>=1.8.0",

    # Code metrics
    "radon>=6.0.0",

    # LLM/AI
    "transformers>=4.38.0",
    "torch>=2.1.0",

    # Information retrieval
    "rank-bm25>=0.2.0",

    # Optimization
    "xgboost>=2.0.0",
]
```

**Install**:
```bash
pip install -e ".[ml]"  # Or use bun
```

---

### Step 2: Create Database Schema

**File**: Create new migration `alembic/versions/029_add_ml_tables.py`

```python
"""Add ML/AI tables for requirement analysis."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    # Requirement embeddings table
    op.create_table(
        'requirement_embeddings',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.func.gen_random_uuid()),
        sa.Column('requirement_id', sa.UUID(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),  # all-MiniLM-L6-v2
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['requirement_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create HNSW index for fast vector search
    op.execute(
        'CREATE INDEX idx_requirement_embedding ON requirement_embeddings USING HNSW (embedding)'
    )

    # Requirement classifications
    op.create_table(
        'requirement_classifications',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.func.gen_random_uuid()),
        sa.Column('requirement_id', sa.UUID(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('priority_score', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('classified_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['requirement_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Extracted entities
    op.create_table(
        'requirement_entities',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.func.gen_random_uuid()),
        sa.Column('requirement_id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_text', sa.String(500), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('extracted_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['requirement_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ML-discovered trace links
    op.create_table(
        'ml_trace_links',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.func.gen_random_uuid()),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('target_id', sa.UUID(), nullable=False),
        sa.Column('link_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('method', sa.String(50), nullable=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['source_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade():
    op.drop_table('ml_trace_links')
    op.drop_table('requirement_entities')
    op.drop_table('requirement_classifications')
    op.drop_table('requirement_embeddings')
```

**Run migration**:
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
alembic upgrade head
```

---

### Step 3: Create Models for New Entities

**File**: `src/tracertm/models/ml_models.py`

```python
"""Models for ML/AI analysis results."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, UUID, func
from sqlalchemy.dialects.postgresql import JSON
from pgvector.sqlalchemy import Vector

from tracertm.models.base import Base


class RequirementEmbedding(Base):
    """Store requirement embeddings for similarity search."""

    __tablename__ = "requirement_embeddings"

    id = Column(UUID, primary_key=True, default=func.gen_random_uuid())
    requirement_id = Column(UUID, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding = Column(Vector(384), nullable=False)  # all-MiniLM-L6-v2 dimension
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RequirementClassification(Base):
    """Store requirement classification results."""

    __tablename__ = "requirement_classifications"

    id = Column(UUID, primary_key=True, default=func.gen_random_uuid())
    requirement_id = Column(UUID, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # functional, non-functional, etc.
    priority_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    classified_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RequirementEntity(Base):
    """Store extracted NER entities from requirements."""

    __tablename__ = "requirement_entities"

    id = Column(UUID, primary_key=True, default=func.gen_random_uuid())
    requirement_id = Column(UUID, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # ACTOR, ACTION, CONDITION, OBJECT
    entity_text = Column(String(500), nullable=False)
    confidence = Column(Float, nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MLTraceLink(Base):
    """Store ML-discovered trace links between items."""

    __tablename__ = "ml_trace_links"

    id = Column(UUID, primary_key=True, default=func.gen_random_uuid())
    source_id = Column(UUID, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type = Column(String(50), nullable=False)  # implements, validates, traces-to
    confidence = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)  # bm25, semantic, codebert, hybrid
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

### Step 4: Create Embedding Service

**File**: `src/tracertm/services/requirement_embeddings_service.py`

```python
"""Requirement embedding service using sentence-transformers."""

import logging
import numpy as np
from typing import Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from tracertm.models.ml_models import RequirementEmbedding
from tracertm.models.item import Item

logger = logging.getLogger(__name__)


class RequirementEmbeddingService:
    """Service for generating and managing requirement embeddings."""

    # Singleton model instance
    _model_instance: Optional[SentenceTransformer] = None

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or load embedding model (lazy loading)."""
        if cls._model_instance is None:
            logger.info("Loading sentence-transformer model: all-MiniLM-L6-v2")
            cls._model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model_instance

    async def embed_requirement(
        self,
        requirement_id: str,
        text: str,
        model_version: str = "1.0"
    ) -> RequirementEmbedding:
        """Generate and store embedding for requirement."""

        # Generate embedding
        model = self.get_model()
        embedding = model.encode(text, convert_to_numpy=True)

        # Store in database
        result = await self.session.execute(
            select(RequirementEmbedding).where(
                RequirementEmbedding.requirement_id == requirement_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.embedding = embedding
            existing.model_version = model_version
        else:
            embedding_record = RequirementEmbedding(
                requirement_id=requirement_id,
                embedding=embedding,
                model_version=model_version,
            )
            self.session.add(embedding_record)

        await self.session.commit()
        await self.session.refresh(existing or embedding_record)
        return existing or embedding_record

    async def find_similar_requirements(
        self,
        query_id: str,
        project_id: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.6
    ) -> list[tuple[str, float]]:
        """Find similar requirements to a given requirement."""

        # Get query embedding
        result = await self.session.execute(
            select(RequirementEmbedding).where(
                RequirementEmbedding.requirement_id == query_id
            )
        )
        query_embedding = result.scalar_one_or_none()

        if not query_embedding:
            return []

        # Find similar embeddings
        query = select(
            RequirementEmbedding,
            Item
        ).join(
            Item,
            RequirementEmbedding.requirement_id == Item.id
        )

        if project_id:
            query = query.where(Item.project_id == project_id)

        result = await self.session.execute(query)
        all_embeddings = result.all()

        similarities = []
        for embedding_record, item in all_embeddings:
            if embedding_record.requirement_id == query_id:
                continue

            sim = cosine_similarity(
                [query_embedding.embedding],
                [embedding_record.embedding]
            )[0][0]

            if sim >= min_similarity:
                similarities.append((item.id, float(sim)))

        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    async def find_duplicate_requirements(
        self,
        project_id: str,
        similarity_threshold: float = 0.85
    ) -> list[tuple[str, str, float]]:
        """Find potential duplicate requirements in project."""

        # Get all embeddings for project
        result = await self.session.execute(
            select(RequirementEmbedding, Item).join(
                Item,
                RequirementEmbedding.requirement_id == Item.id
            ).where(Item.project_id == project_id)
        )
        embeddings = result.all()

        duplicates = []
        for i, (emb1, item1) in enumerate(embeddings):
            for emb2, item2 in embeddings[i+1:]:
                sim = cosine_similarity(
                    [emb1.embedding],
                    [emb2.embedding]
                )[0][0]

                if sim >= similarity_threshold:
                    duplicates.append((item1.id, item2.id, float(sim)))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)
```

---

### Step 5: Create Classification Service

**File**: `src/tracertm/services/requirement_classification_service.py`

```python
"""Requirement classification service using LLM and patterns."""

import logging
from enum import Enum
from typing import Optional

from anthropic import AsyncAnthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.ml_models import RequirementClassification
from tracertm.models.item import Item

logger = logging.getLogger(__name__)


class RequirementCategory(Enum):
    """FURPS+ requirement categories."""
    FUNCTIONAL = "functional"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    SUPPORTABILITY = "supportability"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CONSTRAINT = "constraint"


class RequirementClassificationService:
    """Service for classifying requirements using LLM and patterns."""

    # Pattern-based quick classification
    PATTERN_KEYWORDS = {
        RequirementCategory.PERFORMANCE: [
            "fast", "quick", "latency", "throughput", "response time",
            "millisecond", "second", "performance", "optimize"
        ],
        RequirementCategory.SECURITY: [
            "secure", "encrypt", "authentication", "authorization",
            "password", "token", "certificate", "vulnerability"
        ],
        RequirementCategory.RELIABILITY: [
            "reliable", "available", "uptime", "redundant", "fault",
            "recovery", "availability", "backup"
        ],
        RequirementCategory.USABILITY: [
            "user", "interface", "ui", "ux", "easy", "intuitive",
            "accessible", "simple", "navigation"
        ],
    }

    def __init__(self, session: AsyncSession, api_key: Optional[str] = None):
        """Initialize service."""
        self.session = session
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None

    def _classify_by_patterns(self, text: str) -> Optional[RequirementCategory]:
        """Fast pattern-based classification."""
        text_lower = text.lower()

        for category, keywords in self.PATTERN_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return None

    async def classify_requirement(
        self,
        requirement_id: str,
        title: str,
        description: str,
        use_llm: bool = True
    ) -> RequirementClassification:
        """Classify requirement into FURPS+ category."""

        # Try pattern-based first (fast)
        full_text = f"{title} {description}"
        category = self._classify_by_patterns(full_text)

        confidence = 0.7  # Pattern-based confidence

        # Use LLM if available and needed
        if use_llm and self.client and not category:
            try:
                message = await self.client.messages.create(
                    model="claude-opus-4-20250102",
                    max_tokens=100,
                    system="""Classify the requirement into ONE FURPS+ category.
                    Respond with ONLY the category name: functional, usability,
                    reliability, performance, supportability, security, compliance, or constraint.""",
                    messages=[{
                        "role": "user",
                        "content": f"Title: {title}\nDescription: {description}"
                    }]
                )

                category_text = message.content[0].text.strip().lower()
                try:
                    category = RequirementCategory[category_text.upper()]
                    confidence = 0.95  # LLM-based confidence
                except (KeyError, IndexError):
                    category = RequirementCategory.FUNCTIONAL
                    confidence = 0.5

            except Exception as e:
                logger.error(f"LLM classification failed: {e}")
                if not category:
                    category = RequirementCategory.FUNCTIONAL
                    confidence = 0.3

        if not category:
            category = RequirementCategory.FUNCTIONAL
            confidence = 0.3

        # Store result
        result = await self.session.execute(
            select(RequirementClassification).where(
                RequirementClassification.requirement_id == requirement_id
            )
        )
        classification = result.scalar_one_or_none()

        if classification:
            classification.category = category.value
            classification.confidence = confidence
        else:
            classification = RequirementClassification(
                requirement_id=requirement_id,
                category=category.value,
                confidence=confidence
            )
            self.session.add(classification)

        await self.session.commit()
        await self.session.refresh(classification)
        return classification

    async def get_classification(
        self,
        requirement_id: str
    ) -> Optional[RequirementClassification]:
        """Get existing classification."""
        result = await self.session.execute(
            select(RequirementClassification).where(
                RequirementClassification.requirement_id == requirement_id
            )
        )
        return result.scalar_one_or_none()
```

---

### Step 6: Create Duplicate Detection Service

**File**: `src/tracertm/services/requirement_duplicate_detector.py`

```python
"""Duplicate requirement detection using SimHash."""

import logging
from typing import Optional
from uuid import UUID

from simhash import SimHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item

logger = logging.getLogger(__name__)


class RequirementDuplicateDetector:
    """Detect duplicate and near-duplicate requirements using SimHash."""

    def __init__(
        self,
        session: AsyncSession,
        similarity_threshold: int = 3
    ):
        """Initialize detector.

        Args:
            session: Database session
            similarity_threshold: Hamming distance threshold (0-64)
                - 0-2: Exact duplicates
                - 3-5: Very similar (90%+ overlap)
                - 6-10: Similar (75%+ overlap)
                - 11-20: Loose similarity
        """
        self.session = session
        self.threshold = similarity_threshold
        self.fingerprints: dict[str, SimHash] = {}

    async def index_requirements(self, project_id: str) -> None:
        """Index all requirements in a project."""
        result = await self.session.execute(
            select(Item).where(Item.project_id == project_id)
        )
        items = result.scalars().all()

        for item in items:
            text = f"{item.title} {item.description or ''}".lower()
            self.fingerprints[item.id] = SimHash(text)

        logger.info(f"Indexed {len(self.fingerprints)} requirements")

    async def find_duplicates(
        self,
        requirement_text: str,
        project_id: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> list[tuple[str, int]]:
        """Find duplicate/near-duplicate requirements.

        Returns: List of (requirement_id, hamming_distance) sorted by distance
        """
        query_hash = SimHash(requirement_text.lower())

        # Index project if not already done
        if not self.fingerprints and project_id:
            await self.index_requirements(project_id)

        results = []
        for req_id, stored_hash in self.fingerprints.items():
            if exclude_id and req_id == exclude_id:
                continue

            distance = query_hash.distance(stored_hash)
            if distance <= self.threshold:
                results.append((req_id, distance))

        return sorted(results, key=lambda x: x[1])

    def get_statistics(self) -> dict:
        """Get fingerprint statistics."""
        if len(self.fingerprints) < 2:
            return {"total_requirements": len(self.fingerprints)}

        distances = []
        hashes = list(self.fingerprints.values())

        for i in range(len(hashes)):
            for j in range(i + 1, len(hashes)):
                distances.append(hashes[i].distance(hashes[j]))

        return {
            "total_requirements": len(self.fingerprints),
            "avg_distance": sum(distances) / len(distances) if distances else 0,
            "min_distance": min(distances) if distances else 0,
            "max_distance": max(distances) if distances else 0,
            "comparison_pairs": len(distances)
        }
```

---

### Step 7: Create API Routes

**File**: `src/tracertm/api/routers/ml_analysis.py`

```python
"""API routes for ML/AI analysis endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.models.item import Item
from tracertm.services.requirement_embeddings_service import RequirementEmbeddingService
from tracertm.services.requirement_classification_service import RequirementClassificationService
from tracertm.services.requirement_duplicate_detector import RequirementDuplicateDetector

router = APIRouter(prefix="/api/v1/ml", tags=["ml-analysis"])


@router.post("/embeddings/{item_id}")
async def generate_embedding(
    item_id: str,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Generate and store embedding for requirement."""

    # Get requirement
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Generate embedding
    service = RequirementEmbeddingService(session)
    text = f"{item.title} {item.description or ''}"
    embedding = await service.embed_requirement(item_id, text)

    return {
        "requirement_id": str(embedding.requirement_id),
        "model_version": embedding.model_version,
        "created_at": embedding.created_at.isoformat()
    }


@router.get("/similar/{item_id}")
async def find_similar_requirements(
    item_id: str,
    project_id: Optional[str] = None,
    top_k: int = 5,
    min_similarity: float = 0.6,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Find similar requirements using embeddings."""

    service = RequirementEmbeddingService(session)
    similar = await service.find_similar_requirements(
        item_id,
        project_id,
        top_k,
        min_similarity
    )

    return {
        "query_id": item_id,
        "similar_requirements": [
            {"requirement_id": req_id, "similarity": similarity}
            for req_id, similarity in similar
        ]
    }


@router.get("/duplicates/{project_id}")
async def find_duplicates(
    project_id: str,
    similarity_threshold: float = 0.85,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Find duplicate requirements in project."""

    service = RequirementEmbeddingService(session)
    duplicates = await service.find_duplicate_requirements(
        project_id,
        similarity_threshold
    )

    return {
        "project_id": project_id,
        "duplicates": [
            {
                "requirement_1": req1_id,
                "requirement_2": req2_id,
                "similarity": similarity
            }
            for req1_id, req2_id, similarity in duplicates
        ],
        "count": len(duplicates)
    }


@router.post("/classify/{item_id}")
async def classify_requirement(
    item_id: str,
    use_llm: bool = True,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Classify requirement into FURPS+ category."""

    # Get requirement
    item = await session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Classify
    service = RequirementClassificationService(session)
    classification = await service.classify_requirement(
        item_id,
        item.title,
        item.description or "",
        use_llm
    )

    return {
        "requirement_id": str(classification.requirement_id),
        "category": classification.category,
        "confidence": classification.confidence,
        "classified_at": classification.classified_at.isoformat()
    }


@router.post("/batch-analyze/{project_id}")
async def batch_analyze_project(
    project_id: str,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """Analyze all requirements in project."""

    from sqlalchemy import select

    # Get all requirements
    result = await session.execute(
        select(Item).where(Item.project_id == project_id)
    )
    items = result.scalars().all()

    embedding_service = RequirementEmbeddingService(session)
    classification_service = RequirementClassificationService(session)

    analyzed = 0
    for item in items:
        text = f"{item.title} {item.description or ''}"

        # Generate embedding
        await embedding_service.embed_requirement(item.id, text)

        # Classify
        await classification_service.classify_requirement(
            item.id,
            item.title,
            item.description or ""
        )

        analyzed += 1

    return {
        "project_id": project_id,
        "requirements_analyzed": analyzed,
        "embeddings_generated": analyzed,
        "classifications": analyzed
    }
```

---

### Step 8: Update Main API Router

**File**: `src/tracertm/api/main.py`

```python
# Add to imports
from tracertm.api.routers import ml_analysis

# Add to app setup
app.include_router(ml_analysis.router)
```

---

### Step 9: Create Tests

**File**: `tests/integration/test_ml_services.py`

```python
"""Integration tests for ML services."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.services.requirement_embeddings_service import RequirementEmbeddingService
from tracertm.services.requirement_classification_service import RequirementClassificationService
from tracertm.services.requirement_duplicate_detector import RequirementDuplicateDetector


@pytest.mark.asyncio
async def test_embedding_generation(db_session: AsyncSession):
    """Test embedding generation."""

    # Create requirement
    item = Item(
        id="test-req-1",
        project_id="test-project",
        title="User login",
        description="User should be able to login with email and password"
    )
    db_session.add(item)
    await db_session.commit()

    # Generate embedding
    service = RequirementEmbeddingService(db_session)
    embedding = await service.embed_requirement(
        "test-req-1",
        "User login: User should be able to login with email and password"
    )

    assert embedding.requirement_id == "test-req-1"
    assert embedding.embedding is not None
    assert len(embedding.embedding) == 384  # all-MiniLM-L6-v2 dimension


@pytest.mark.asyncio
async def test_requirement_classification(db_session: AsyncSession):
    """Test requirement classification."""

    # Create requirement
    item = Item(
        id="test-req-2",
        project_id="test-project",
        title="Fast login",
        description="System must respond to login within 100ms"
    )
    db_session.add(item)
    await db_session.commit()

    # Classify
    service = RequirementClassificationService(db_session)
    classification = await service.classify_requirement(
        "test-req-2",
        item.title,
        item.description or "",
        use_llm=False
    )

    assert classification.requirement_id == "test-req-2"
    assert classification.category in [e.value for e in RequirementClassificationService.__dict__.get("RequirementCategory", {}).values()]


@pytest.mark.asyncio
async def test_duplicate_detection(db_session: AsyncSession):
    """Test duplicate detection."""

    # Create similar requirements
    items = [
        Item(
            id="test-dup-1",
            project_id="test-project",
            title="Create user",
            description="User should be able to create a new account"
        ),
        Item(
            id="test-dup-2",
            project_id="test-project",
            title="Create account",
            description="Users must be able to create new accounts"
        ),
    ]

    for item in items:
        db_session.add(item)
    await db_session.commit()

    # Find duplicates
    detector = RequirementDuplicateDetector(db_session)
    await detector.index_requirements("test-project")

    text = "User can create a new account"
    duplicates = await detector.find_duplicates(text, "test-project")

    assert len(duplicates) > 0
```

---

## Deployment Checklist

- [ ] Update `pyproject.toml` with ML dependencies
- [ ] Run migration: `alembic upgrade head`
- [ ] Create all service files
- [ ] Create API routes
- [ ] Write tests
- [ ] Update main.py to include new routes
- [ ] Test embeddings with sample data
- [ ] Test API endpoints
- [ ] Monitor performance in staging
- [ ] Add monitoring/observability
- [ ] Document in API docs
- [ ] Deploy to production

---

## Environment Variables

Add to `.env`:

```bash
# LLM settings (optional)
ANTHROPIC_API_KEY=sk-ant-...

# ML settings
ML_EMBEDDING_MODEL=all-MiniLM-L6-v2
ML_ENABLE_LLM_QUALITY=true
ML_ENABLE_DUPLICATE_DETECTION=true
ML_SIMHASH_THRESHOLD=5
```

---

## Performance Tuning

### Batch Embeddings

```python
# Instead of embedding one at a time
embeddings = model.encode(list_of_texts)  # Vectorized!
```

### Use GPU (if available)

```python
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
```

### Cache Models

Already implemented in service via singleton pattern.

---

## Next Steps

1. Follow steps 1-9 above in order
2. Run tests after each step
3. Deploy to staging environment
4. Monitor performance
5. Iterate based on feedback
6. Scale to production

---

**Time Estimate**:
- Steps 1-4: 2 hours
- Steps 5-6: 1 hour
- Steps 7-8: 2 hours
- Tests + fixes: 2 hours
- Total: ~7 hours for full MVP

**Difficulty**: Medium (mostly copy-paste with some customization)
