"""Requirement Quality Service for TraceRTM.

Functional Requirements: FR-QUAL-001
"""

import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.requirement_quality import RequirementQuality

# Simple regex-based smell detection patterns
SMELL_PATTERNS = {
    "superlative": r"\b(best|fastest|highest|lowest|most|least|optimal|maximize|minimize)\b",
    "comparative": r"\b(better|faster|cheaper|easier|harder|more|less)\b",
    "subjective": r"\b(user-friendly|easy to use|simple|efficient|flexible|robust|seamless)\b",
    "loopholes": r"\b(if possible|if applicable|as appropriate|may|might|should)\b",
    "ambiguous_adverbs": r"\b(usually|often|normally|typically|generally|approximately)\b",
    "negative_statements": r"\b(not|never|no|none)\b",
    "vague_pronouns": r"\b(it|this|that|these|those)\b",
    "open_ended": r"\b(et cetera|etc\.|and so on|including but not limited to)\b",
    "incomplete_references": r"\b(tbd|tba|to be defined|to be determined|see documentation)\b",
}


class RequirementQualityService:
    """Service for Requirement Quality Analysis."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def analyze_quality(self, item_id: str) -> RequirementQuality:
        """Analyze requirement quality and save/update results."""
        # Get the item text
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        text = f"{item.title} {item.description or ''}".lower()

        # Detect smells
        detected_smells = []
        suggestions = []

        for smell_type, pattern in SMELL_PATTERNS.items():
            if re.search(pattern, text):
                detected_smells.append(smell_type)
                suggestions.append(f"Found {smell_type} terms. Consider rephrasing to be more specific.")

        # Calculate scores (simple heuristic)
        # Ambiguity increases with more smells
        ambiguity_score = min(1.0, len(detected_smells) * 0.15)

        # Completeness decreases with certain smells
        completeness_penalty = 0.0
        if "incomplete_references" in detected_smells:
            completeness_penalty += 0.3
        if "loopholes" in detected_smells:
            completeness_penalty += 0.2

        completeness_score = max(0.0, 1.0 - completeness_penalty)

        # Check if analysis exists
        result = await self.session.execute(select(RequirementQuality).where(RequirementQuality.item_id == item_id))
        quality_record = result.scalar_one_or_none()

        if quality_record:
            quality_record.smells = detected_smells
            quality_record.ambiguity_score = ambiguity_score
            quality_record.completeness_score = completeness_score
            quality_record.suggestions = suggestions
            quality_record.last_analyzed_at = datetime.now(UTC)
            quality_record.version += 1
        else:
            quality_record = RequirementQuality(
                item_id=item_id,
                smells=detected_smells,
                ambiguity_score=ambiguity_score,
                completeness_score=completeness_score,
                suggestions=suggestions,
                last_analyzed_at=datetime.now(UTC),
            )
            self.session.add(quality_record)

        await self.session.commit()
        await self.session.refresh(quality_record)
        return quality_record

    async def get_quality(self, item_id: str) -> RequirementQuality | None:
        """Get quality record for an item."""
        result = await self.session.execute(select(RequirementQuality).where(RequirementQuality.item_id == item_id))
        return result.scalar_one_or_none()
