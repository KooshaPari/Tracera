"""TF-IDF cosine similarity scorer with graceful fallback.

Implements a TF-IDF based agreement scorer that uses sklearn's TfidfVectorizer
and cosine similarity when available. Falls back to JaccardScorer if sklearn is
not installed.
"""

from __future__ import annotations

from tracertm.ports.scorer import ScoreResult, ScorerPort
from tracertm.scoring.jaccard_scorer import JaccardScorer

_SKLEARN_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    _SKLEARN_AVAILABLE = True
except ImportError:
    pass


class TFIDFScorer:
    """TF-IDF cosine similarity scorer.

    Computes agreement using TF-IDF (Term Frequency-Inverse Document Frequency)
    representation and cosine similarity. Requires scikit-learn.

    If scikit-learn is not available, falls back to JaccardScorer transparently.

    Implements :class:`ScorerPort` protocol:
        - ``name`` property: returns "tfidf" (or "jaccard" if fallback is active)
        - ``score(requirement_text, artifact_text) -> ScoreResult``
    """

    def __init__(self) -> None:
        """Initialize the TF-IDF scorer."""
        self._use_sklearn = _SKLEARN_AVAILABLE
        if not self._use_sklearn:
            self._fallback = JaccardScorer()

    @property
    def name(self) -> str:
        """Return the name of the active scorer strategy."""
        return "tfidf" if self._use_sklearn else "jaccard"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        """Return TF-IDF cosine similarity score.

        Args:
            requirement_text: The requirement text to score against.
            artifact_text: The artifact text to compare.

        Returns:
            ScoreResult with normalized score in [0.0, 1.0], rationale, and strategy name.
            If sklearn is unavailable, uses JaccardScorer instead.

        Raises:
            ValueError: If ScoreResult is given an out-of-range value (should not occur).
        """
        if not self._use_sklearn:
            return self._fallback.score(requirement_text, artifact_text)

        # Both empty
        if not requirement_text and not artifact_text:
            return ScoreResult(0.0, "both inputs empty", self.name)

        # One empty
        if not requirement_text or not artifact_text:
            return ScoreResult(0.0, "one or both inputs empty", self.name)

        # Identical inputs
        if requirement_text == artifact_text:
            return ScoreResult(1.0, "inputs are identical", self.name)

        try:
            # Build TF-IDF vectors for both documents
            vectorizer = TfidfVectorizer(
                lowercase=True, stop_words=None, token_pattern=r"[A-Za-z0-9]+"
            )
            # Fit on both documents to build vocabulary
            tfidf_matrix = vectorizer.fit_transform(
                [requirement_text, artifact_text]
            )

            # Compute cosine similarity between the two vectors
            similarity = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2]
            )[0][0]

            # Normalize to [0.0, 1.0]
            score = float(similarity)
            score = round(max(0.0, min(1.0, score)), 6)

            # Get feature names for rationale
            feature_names = vectorizer.get_feature_names_out()
            top_features = sorted(feature_names[:10])
            rationale = (
                f"TF-IDF cosine similarity {score:.4f} "
                f"(top features: {', '.join(top_features[:5])})"
            )

            return ScoreResult(score, rationale, self.name)

        except Exception as e:
            # If anything fails, fall back to Jaccard
            fallback_result = self._fallback.score(
                requirement_text, artifact_text
            )
            return ScoreResult(
                fallback_result.score,
                f"TF-IDF failed ({e!r}), using fallback: {fallback_result.rationale}",
                "jaccard",
            )
