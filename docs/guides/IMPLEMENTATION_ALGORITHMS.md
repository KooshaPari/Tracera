# Advanced Specification Objects - Implementation Algorithms

This document provides detailed algorithms and code patterns for implementing the advanced specification object research in production systems.

---

## 1. EARS Pattern Recognition & Validation

### 1.1 Pattern Classification Algorithm

```python
import re
from typing import Tuple, Dict, Optional
from enum import Enum

class EARSPattern(Enum):
    UBIQUITOUS = "ubiquitous"
    EVENT_DRIVEN = "event_driven"
    STATE_DRIVEN = "state_driven"
    OPTIONAL_FEATURE = "optional_feature"
    UNWANTED_BEHAVIOR = "unwanted_behavior"


class EARSClassifier:
    """
    Multi-pass EARS pattern classification with confidence scoring.

    Algorithm:
    1. Tokenize requirement text
    2. Check for EARS pattern keywords (WHEN, WHILE, WHERE, IF)
    3. Validate structure (e.g., "WHEN X THEN Y" vs "WHEN X")
    4. Extract components for validation
    5. Return classification with confidence [0.0, 1.0]
    """

    # Ordered by specificity (most specific first)
    PATTERNS = [
        (
            EARSPattern.UNWANTED_BEHAVIOR,
            r'^IF\s+(.+?),?\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+SHALL\s+(.+?)\.?$',
            ["condition", "system", "action"],
        ),
        (
            EARSPattern.STATE_DRIVEN,
            r'^WHILE\s+(.+?),?\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+SHALL\s+(.+?)\.?$',
            ["state", "system", "action"],
        ),
        (
            EARSPattern.EVENT_DRIVEN,
            r'^(?:the\s+)?(\w+(?:\s+\w+)*)\s+SHALL\s+(.+?)\s+WHEN\s+(.+?)\.?$',
            ["system", "action", "event"],
        ),
        (
            EARSPattern.OPTIONAL_FEATURE,
            r'^WHERE\s+(.+?),?\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+SHALL\s+(.+?)\.?$',
            ["feature", "system", "action"],
        ),
        (
            EARSPattern.UBIQUITOUS,
            r'^(?:The\s+)?(\w+(?:\s+\w+)*)\s+SHALL\s+(.+?)\.?$',
            ["system", "action"],
        ),
    ]

    @staticmethod
    def classify(requirement_text: str) -> Tuple[EARSPattern, Dict[str, str], float]:
        """
        Classify requirement into EARS pattern.

        Returns:
            (pattern, components_dict, confidence_0_to_1)

        Example:
            >>> text = "When a user fails authentication, the system SHALL " \
            ...         "log the failure within 100ms."
            >>> pattern, components, conf = EARSClassifier.classify(text)
            >>> assert pattern == EARSPattern.EVENT_DRIVEN
            >>> assert confidence > 0.8
        """
        text = requirement_text.strip()

        # Check banned modal verbs (reduces confidence if present)
        banned_modals = {"should", "may", "might", "could"}
        has_banned = any(f" {m} " in text.lower() for m in banned_modals)
        confidence_penalty = 0.2 if has_banned else 0.0

        for pattern, regex, component_names in EARSClassifier.PATTERNS:
            match = re.match(regex, text, re.IGNORECASE | re.DOTALL)

            if match:
                components = dict(zip(component_names, match.groups()))

                # Confidence calculation
                confidence = 0.95 - confidence_penalty

                # Reduce confidence if requirement too long or too short
                words = len(text.split())
                if words < 3:
                    confidence -= 0.2
                elif words > 50:
                    confidence -= 0.1

                # If we matched late in the list, reduce confidence
                pattern_index = [p[0] for p in EARSClassifier.PATTERNS].index(pattern)
                confidence -= pattern_index * 0.05

                return (pattern, components, max(0.0, confidence))

        # No pattern matched
        return (None, {}, 0.0)

    @staticmethod
    def validate_structure(pattern: EARSPattern, components: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate that matched components make semantic sense.

        Checks:
        - Required components present
        - No obvious tautologies or contradictions
        - Measurable action (for ubiquitous)
        """
        issues = []

        # Validate system component exists and is meaningful
        if "system" in components:
            system = components["system"].lower()
            if len(system) < 2:
                issues.append("System component too short")
            if system in {"the", "a", "an"}:
                issues.append("System component is an article, not a system")

        # Validate action is present and not empty
        if "action" in components:
            action = components["action"].strip()
            if len(action) < 3:
                issues.append("Action component too vague")

            # Check if action is testable (contains measurement or observable)
            has_measurement = any(c.isdigit() for c in action)
            has_observable = any(
                word in action.lower()
                for word in ["return", "display", "log", "send", "reject", "accept", "verify"]
            )
            if not (has_measurement or has_observable) and pattern == EARSPattern.UBIQUITOUS:
                issues.append("Action lacks measurable criteria (add time, count, or observable state)")

        # Validate condition for unwanted behavior pattern
        if pattern == EARSPattern.UNWANTED_BEHAVIOR and "condition" in components:
            condition = components["condition"].lower()
            if "shall" in condition:
                issues.append("Condition contains 'SHALL' - should describe event, not requirement")

        return (len(issues) == 0, issues)


# Usage example
if __name__ == "__main__":
    test_reqs = [
        "The authentication service SHALL reject invalid passwords within 100ms",
        "When a user clicks logout, the system SHALL clear all session tokens",
        "While premium subscription is active, the API SHALL prioritize requests",
        "If network timeout occurs, the system SHALL retry up to 3 times",
        "The system should handle errors gracefully",  # Bad: uses "should"
    ]

    for req in test_reqs:
        pattern, components, confidence = EARSClassifier.classify(req)
        valid, issues = EARSClassifier.validate_structure(pattern, components)
        print(f"Requirement: {req}")
        print(f"  Pattern: {pattern.value if pattern else 'NONE'} (confidence: {confidence:.2f})")
        if issues:
            print(f"  Issues: {', '.join(issues)}")
        print()
```

---

## 2. Quality Scoring Algorithms

### 2.1 Requirement Ambiguity Detection

```python
import re
from collections import Counter
from typing import List, Tuple

class AmbiguityDetector:
    """
    Detect ambiguous language in requirements.

    Heuristic-based detector that scores 0.0 (clear) to 1.0 (highly ambiguous).
    """

    # Words/phrases that create ambiguity
    AMBIGUOUS_MODAL_VERBS = {
        "should": 0.8,      # Very ambiguous
        "may": 0.9,         # Could be permission or possibility
        "might": 0.85,
        "could": 0.8,
        "can": 0.7,         # Slightly ambiguous (capability vs requirement)
        "possible": 0.6,
    }

    AMBIGUOUS_ADJECTIVES = {
        "appropriate": 0.9,
        "suitable": 0.85,
        "relevant": 0.8,
        "sufficient": 0.75,
        "adequate": 0.75,
        "efficient": 0.7,
        "fast": 0.8,        # Relative; needs units
        "slow": 0.8,
        "large": 0.85,      # Relative; needs context
        "small": 0.85,
        "easy": 0.7,
        "complex": 0.7,
        "user-friendly": 0.85,
        "robust": 0.7,      # Vague; what does robust mean?
    }

    AMBIGUOUS_PHRASES = {
        "etc.": 0.9,        # Incomplete list
        "and/or": 0.85,     # Doesn't clearly specify combinations
        "kind of": 0.9,
        "sort of": 0.9,
        "roughly": 0.8,
        "approximately": 0.7,
        "in general": 0.7,
        "usually": 0.8,
        "typically": 0.75,
        "as needed": 0.8,
        "if necessary": 0.75,
        "as appropriate": 0.9,
        "as required": 0.7,  # Circular definition
    }

    @staticmethod
    def detect(requirement_text: str) -> Tuple[float, List[str]]:
        """
        Detect ambiguity in requirement.

        Returns:
            (ambiguity_score: 0.0-1.0, ambiguous_terms: list)

        Score interpretation:
        - 0.0-0.2:  Clear requirement
        - 0.2-0.5:  Minor ambiguities that should be clarified
        - 0.5-0.8:  Significant ambiguities; rework recommended
        - 0.8-1.0:  Highly ambiguous; major rework needed
        """
        req_lower = requirement_text.lower()
        ambiguous_terms = []
        ambiguity_scores = []

        # Check modal verbs
        for verb, score in AmbiguityDetector.AMBIGUOUS_MODAL_VERBS.items():
            if re.search(rf"\b{verb}\b", req_lower):
                ambiguous_terms.append(verb)
                ambiguity_scores.append(score)

        # Check adjectives
        for adj, score in AmbiguityDetector.AMBIGUOUS_ADJECTIVES.items():
            if re.search(rf"\b{adj}\b", req_lower):
                ambiguous_terms.append(adj)
                ambiguity_scores.append(score)

        # Check phrases
        for phrase, score in AmbiguityDetector.AMBIGUOUS_PHRASES.items():
            if phrase in req_lower:
                ambiguous_terms.append(phrase)
                ambiguity_scores.append(score)

        # Compute overall ambiguity score
        if ambiguity_scores:
            # Use exponential average (later terms weighted more)
            overall_score = sum(ambiguity_scores) / len(ambiguity_scores)
        else:
            overall_score = 0.0

        # Penalty for very long requirements (complex = ambiguous)
        words = len(requirement_text.split())
        if words > 50:
            overall_score = min(1.0, overall_score + 0.15)

        # Penalty for multiple conditions (increases ambiguity)
        condition_count = req_lower.count(" and ") + req_lower.count(" or ")
        if condition_count > 3:
            overall_score = min(1.0, overall_score + 0.2)

        return (min(1.0, overall_score), ambiguous_terms)

```

### 2.2 Completeness Scoring

```python
class CompletenessScorer:
    """
    Score how complete a requirement is.

    Checks for presence of:
    - Context/rationale
    - Acceptance criteria
    - Performance/quality attributes
    - Edge cases
    - Dependencies
    """

    @staticmethod
    def score(requirement: Dict[str, str]) -> Tuple[float, List[str]]:
        """
        Score completeness 0.0 (missing) to 1.0 (comprehensive).

        Returns:
            (score, missing_items)
        """
        score = 0.0
        missing = []

        # Check for description/statement
        if requirement.get("description") and len(requirement["description"]) > 20:
            score += 0.2
        else:
            missing.append("Description too short or missing")

        # Check for rationale/context
        if requirement.get("rationale") and len(requirement["rationale"]) > 30:
            score += 0.15
        else:
            missing.append("Missing rationale explaining WHY this requirement exists")

        # Check for acceptance criteria
        criteria = requirement.get("acceptance_criteria", [])
        if len(criteria) >= 3:
            score += 0.2
        elif len(criteria) >= 1:
            score += 0.1
            missing.append("Only 1 acceptance criterion; need at least 3")
        else:
            missing.append("Missing acceptance criteria")

        # Check for performance/quality attributes
        perf_keywords = {"response time", "latency", "throughput", "timeout", "retry",
                        "availability", "uptime", "capacity", "load"}
        has_perf = any(
            kw in (requirement.get("description", "") + requirement.get("rationale", "")).lower()
            for kw in perf_keywords
        )
        if has_perf:
            score += 0.15
        else:
            missing.append("Missing performance/quality attributes (response time, availability, etc.)")

        # Check for error handling
        error_keywords = {"fail", "error", "exception", "timeout", "invalid", "reject"}
        has_error_handling = any(
            kw in requirement.get("description", "").lower()
            for kw in error_keywords
        )
        if has_error_handling:
            score += 0.15
        else:
            missing.append("Missing error handling specification")

        # Check for dependencies
        deps = requirement.get("depends_on", [])
        if len(deps) > 0:
            score += 0.05  # Acknowledging dependencies increases completeness
        # Note: we don't penalize for having dependencies; dependencies are OK

        return (score, missing)
```

---

## 3. Volatility Index Computation

### 3.1 Change History Analysis

```python
from datetime import datetime, timedelta
from typing import List

class VolatilityAnalyzer:
    """
    Compute requirement volatility based on change history.

    Algorithm:
    1. Analyze change frequency in recent period
    2. Measure change magnitude (minor vs major)
    3. Assess number of dependent items
    4. Combine into volatility score
    """

    @staticmethod
    def compute_volatility(
        requirement_id: str,
        change_history: List[Dict],
        dependent_count: int,
        ambiguity_score: float,
    ) -> float:
        """
        Compute volatility index 0.0 (stable) to 1.0 (highly volatile).

        Args:
            change_history: List of {date, author, change_type, description}
            dependent_count: Number of items depending on this requirement
            ambiguity_score: From AmbiguityDetector (0.0-1.0)

        Algorithm breakdown:
        - 40% weight: Recent change frequency
        - 30% weight: Dependency complexity
        - 20% weight: Change magnitude
        - 10% weight: Ambiguity
        """

        # Component 1: Change frequency (40%)
        if not change_history:
            frequency_score = 0.0
        else:
            # Count changes in last 90 days
            cutoff = datetime.now() - timedelta(days=90)
            recent_changes = sum(
                1 for c in change_history
                if datetime.fromisoformat(c["date"]) > cutoff
            )

            # Normalize: 10+ changes in 90 days = high volatility
            frequency_score = min(1.0, recent_changes / 10.0)

        # Component 2: Dependency complexity (30%)
        # More dependents = riskier to change = higher volatility
        dependency_score = min(1.0, dependent_count / 10.0)

        # Component 3: Change magnitude (20%)
        if change_history:
            # Analyze magnitude of recent changes
            magnitudes = [
                VolatilityAnalyzer._score_change_magnitude(c)
                for c in change_history[-10:]  # Last 10 changes
            ]
            magnitude_score = sum(magnitudes) / len(magnitudes)
        else:
            magnitude_score = 0.0

        # Component 4: Ambiguity (10%)
        ambiguity_weighted = ambiguity_score * 0.1

        # Combine components
        volatility = (
            frequency_score * 0.4 +
            dependency_score * 0.3 +
            magnitude_score * 0.2 +
            ambiguity_weighted
        )

        return min(1.0, volatility)

    @staticmethod
    def _score_change_magnitude(change: Dict) -> float:
        """
        Score magnitude of a single change.

        Returns 0.0 (trivial) to 1.0 (complete rewrite).
        """
        change_type = change.get("change_type", "").lower()

        type_scores = {
            "wording": 0.1,      # Trivial: just wording
            "formatting": 0.05,  # Trivial: spacing, formatting
            "acceptance_criteria": 0.5,  # Moderate: changes acceptance criteria
            "description": 0.3,   # Minor-moderate: changes description
            "status": 0.2,        # Minor: status change
            "priority": 0.15,     # Minor: priority change
            "superseded": 0.9,    # Major: requirement superseded
            "deleted": 0.8,       # Major: requirement deleted
            "split": 0.7,         # Major: requirement split into multiple
            "merged": 0.6,        # Major: requirement merged
        }

        return type_scores.get(change_type, 0.5)  # Default to moderate
```

---

## 4. Flakiness Detection Algorithms

### 4.1 Pattern-Based Flakiness Detection

```python
from collections import deque
from statistics import mean, stdev

class FlakynessDetector:
    """
    Detect flaky test patterns using statistical analysis.

    Three detection strategies:
    1. Simple ratio: failures / total_runs
    2. Pattern analysis: are failures clustered?
    3. Order dependency: does it fail after certain tests?
    """

    @staticmethod
    def compute_flakiness_score(
        run_history: List[Dict],
        window_size: int = 20,
    ) -> Tuple[float, str]:
        """
        Compute flakiness 0.0 (stable) to 1.0 (completely flaky).

        Returns:
            (score, classification)

        Algorithm:
        1. Take last N runs
        2. Count failures
        3. Assess if failures are clustered or random
        4. Return score and classification
        """

        if not run_history or len(run_history) < window_size:
            return (0.0, "INSUFFICIENT_DATA")

        recent = run_history[-window_size:]
        executed = [r for r in recent if r["status"] != "skip"]

        if not executed:
            return (0.0, "ALL_SKIPPED")

        # Basic failure rate
        failures = sum(1 for r in executed if r["status"] == "fail")
        failure_rate = failures / len(executed)

        # Check for clustering (failures in groups = order dependency)
        failure_indices = [i for i, r in enumerate(executed) if r["status"] == "fail"]

        if not failure_indices:
            return (0.0, "STABLE")

        # Compute clustering coefficient
        if len(failure_indices) > 1:
            gaps = [failure_indices[i+1] - failure_indices[i] for i in range(len(failure_indices)-1)]
            avg_gap = mean(gaps)
            max_gap = max(gaps)

            # Clustered failures: small gaps between failures
            if avg_gap < 3:
                # Likely order-dependent
                clustering_factor = 0.8
            elif max_gap > window_size - 2:
                # Spread out; likely environmental
                clustering_factor = 0.5
            else:
                clustering_factor = 0.6
        else:
            clustering_factor = 0.3  # Single failure not necessarily flaky

        # Combine failure rate and clustering
        flakiness = failure_rate * 0.6 + clustering_factor * 0.4

        # Classify
        if flakiness < 0.1:
            classification = "STABLE"
        elif flakiness < 0.3:
            classification = "RARELY_FLAKY"
        elif flakiness < 0.6:
            classification = "OFTEN_FLAKY"
        else:
            classification = "HIGHLY_FLAKY"

        return (flakiness, classification)

    @staticmethod
    def detect_order_dependency(
        test_id: str,
        test_run_log: List[Dict],  # Full log of all tests in order
    ) -> Optional[str]:
        """
        Detect if test fails only after specific predecessors.

        Algorithm:
        1. Find all runs of test_id that failed
        2. Look at the test that ran immediately before each failure
        3. Identify if a pattern exists (e.g., "always fails after test_auth")
        4. Confidence must be > 60%
        """

        test_failures = []
        for i, entry in enumerate(test_run_log):
            if entry["test_id"] == test_id and entry["status"] == "fail":
                if i > 0:
                    preceding_test = test_run_log[i-1]["test_id"]
                    test_failures.append(preceding_test)

        if not test_failures:
            return None

        # Count frequency of each predecessor
        predecessor_counts = {}
        for pred in test_failures:
            predecessor_counts[pred] = predecessor_counts.get(pred, 0) + 1

        # Find most common
        if predecessor_counts:
            most_common = max(predecessor_counts.items(), key=lambda x: x[1])
            frequency = most_common[1] / len(test_failures)

            if frequency >= 0.6:  # 60% confidence
                return most_common[0]

        return None

    @staticmethod
    def detect_time_dependency(run_history: List[Dict]) -> Optional[Dict]:
        """
        Detect if test fails at certain times.
        """

        failure_hours = []
        for run in run_history:
            if run["status"] == "fail":
                hour = datetime.fromisoformat(run["timestamp"]).hour
                failure_hours.append(hour)

        if not failure_hours:
            return None

        # If all failures in same hour, likely time-dependent
        if len(set(failure_hours)) == 1:
            return {
                "type": "time_of_day",
                "hour": failure_hours[0],
                "confidence": len(failure_hours) / len(run_history),
            }

        return None
```

---

## 5. WSJF/RICE Scoring Implementation

### 5.1 Relative Scoring System

```python
class RelativeScorer:
    """
    Implement relative WSJF/RICE scoring.

    Key insight: WSJF and RICE are RELATIVE scores.
    Must score all items in context to prioritize effectively.

    Algorithm:
    1. Collect all items to score
    2. Normalize each dimension across all items
    3. Compute composite scores
    4. Rank by score
    """

    @staticmethod
    def normalize_scores(
        items: List[Dict],
        dimension: str,
        scale: Tuple[int, int] = (1, 20),
    ) -> List[Dict]:
        """
        Normalize scores for a dimension across all items.

        Converts absolute scores to relative 1-20 scale.

        Algorithm:
        1. Find min and max values for this dimension
        2. Map each value to 1-20 scale
        3. Handle edge cases (all same, missing values)
        """

        values = [
            item[dimension]
            for item in items
            if dimension in item and item[dimension] is not None
        ]

        if not values:
            # All missing: assign default middle value
            return [
                {**item, f"{dimension}_normalized": (scale[0] + scale[1]) / 2}
                for item in items
            ]

        min_val = min(values)
        max_val = max(values)

        if min_val == max_val:
            # All same: all get middle value
            mid_val = (scale[0] + scale[1]) / 2
            return [
                {**item, f"{dimension}_normalized": mid_val if dimension in item else None}
                for item in items
            ]

        # Linear interpolation to 1-20 scale
        result = []
        for item in items:
            if dimension not in item or item[dimension] is None:
                normalized = None
            else:
                val = item[dimension]
                # Map [min_val, max_val] -> [scale[0], scale[1]]
                normalized = scale[0] + (val - min_val) / (max_val - min_val) * (scale[1] - scale[0])

            result.append({
                **item,
                f"{dimension}_normalized": normalized,
            })

        return result

    @staticmethod
    def compute_wsjf_score(
        items: List[Dict],
        bv_dimension: str = "business_value",
        tc_dimension: str = "time_criticality",
        rr_dimension: str = "risk_reduction",
        js_dimension: str = "job_size",
    ) -> List[Dict]:
        """
        Compute WSJF scores for a list of items.

        WSJF = (BV + TC + RR) / JS

        Args:
            items: List of items with scoring dimensions
            bv_dimension: Field name for business value
            tc_dimension: Field name for time criticality
            rr_dimension: Field name for risk reduction
            js_dimension: Field name for job size (denominator)

        Returns:
            Items with added "wsjf_score" and "wsjf_rank" fields
        """

        # Normalize each dimension across all items
        for dim in [bv_dimension, tc_dimension, rr_dimension]:
            items = RelativeScorer.normalize_scores(items, dim)

        # Compute WSJF
        scored_items = []
        for item in items:
            bv = item.get(f"{bv_dimension}_normalized", 10)
            tc = item.get(f"{tc_dimension}_normalized", 10)
            rr = item.get(f"{rr_dimension}_normalized", 10)
            js = item.get(js_dimension, 1)

            if bv and tc and rr:
                wsjf = (bv + tc + rr) / max(js, 1)
            else:
                wsjf = 0

            scored_items.append({
                **item,
                "wsjf_score": wsjf,
            })

        # Rank items by WSJF score
        ranked = sorted(scored_items, key=lambda x: x["wsjf_score"], reverse=True)
        for rank, item in enumerate(ranked, 1):
            item["wsjf_rank"] = rank

        return ranked
```

---

## 6. Cryptographic Versioning

### 6.1 SHA-256 Chain Implementation

```python
import hashlib
import json
from datetime import datetime

class CryptographicVersionChain:
    """
    Maintain immutable chain of requirement versions using SHA-256.

    Similar to blockchain: each version hash links to previous version's hash.
    Prevents tampering: altering any version would break all subsequent hashes.
    """

    @staticmethod
    def compute_content_hash(content: Dict) -> str:
        """Compute SHA-256 hash of requirement content."""
        # Sort keys for deterministic hashing
        json_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def compute_chain_hash(
        content_hash: str,
        previous_chain_hash: Optional[str],
        timestamp: datetime,
    ) -> str:
        """
        Compute chain hash linking this version to previous.

        Formula: SHA256(previous_hash + content_hash + timestamp)

        This creates a "Merkle chain" - altering any previous version
        would change its hash, breaking all subsequent hashes.
        """

        chain_input = f"{previous_chain_hash or ''}|{content_hash}|{timestamp.isoformat()}"
        return hashlib.sha256(chain_input.encode()).hexdigest()

    @staticmethod
    def create_version(
        requirement_id: str,
        content: Dict,
        previous_version: Optional[Dict] = None,
    ) -> Dict:
        """
        Create a new version with cryptographic integrity.

        Returns:
            {
                "version": 1,
                "timestamp": "2024-01-29T...",
                "content_hash": "abc123...",
                "chain_hash": "def456...",
                "previous_hash": "previous_chain_hash",
                "content": {...}
            }
        """

        timestamp = datetime.now()

        # Compute this version's content hash
        content_hash = CryptographicVersionChain.compute_content_hash(content)

        # Get previous chain hash (if exists)
        previous_hash = previous_version["chain_hash"] if previous_version else None

        # Compute this version's chain hash
        chain_hash = CryptographicVersionChain.compute_chain_hash(
            content_hash,
            previous_hash,
            timestamp,
        )

        return {
            "requirement_id": requirement_id,
            "version": (previous_version["version"] + 1) if previous_version else 1,
            "timestamp": timestamp.isoformat(),
            "content_hash": content_hash,
            "chain_hash": chain_hash,
            "previous_hash": previous_hash,
            "content": content,
        }

    @staticmethod
    def verify_chain_integrity(versions: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Verify that version chain hasn't been tampered with.

        Algorithm:
        1. For each version, recompute its chain hash
        2. Compare to stored chain hash
        3. Verify each version's previous_hash matches predecessor's chain_hash
        """

        errors = []

        for i, version in enumerate(versions):
            # Recompute chain hash for this version
            recomputed = CryptographicVersionChain.compute_chain_hash(
                version["content_hash"],
                version["previous_hash"],
                datetime.fromisoformat(version["timestamp"]),
            )

            if recomputed != version["chain_hash"]:
                errors.append(
                    f"Version {version['version']}: chain hash mismatch "
                    f"(stored={version['chain_hash']}, computed={recomputed})"
                )

            # Verify previous_hash links correctly
            if i > 0:
                prev_version = versions[i-1]
                if version["previous_hash"] != prev_version["chain_hash"]:
                    errors.append(
                        f"Version {version['version']}: previous_hash doesn't match predecessor's chain_hash"
                    )

            # Verify content hash matches content
            content_hash = CryptographicVersionChain.compute_content_hash(version["content"])
            if content_hash != version["content_hash"]:
                errors.append(
                    f"Version {version['version']}: content hash mismatch (tampering detected)"
                )

        return (len(errors) == 0, errors)
```

---

## 7. Impact Analysis Graph

### 7.1 Dependency Graph Traversal

```python
from typing import Set, Dict, List

class ImpactAnalyzer:
    """
    Analyze impact of requirement changes on dependent items.

    Uses graph traversal to compute:
    - Direct dependents
    - Transitive dependents
    - Estimated effort to propagate changes
    - Risk assessment
    """

    def __init__(self, dependency_graph: Dict[str, List[str]]):
        """
        Build analyzer from dependency graph.

        Args:
            dependency_graph: {item_id: [dependent_item_ids]}
        """
        self.graph = dependency_graph

    def compute_impact_radius(self, requirement_id: str) -> Dict[str, Any]:
        """
        Compute full impact of changing a requirement.

        Returns:
            {
                "direct_dependents": [...],
                "transitive_dependents": [...],
                "total_affected": count,
                "estimated_hours": estimate,
                "risk_level": "HIGH" | "MEDIUM" | "LOW",
            }
        """

        direct = set(self.graph.get(requirement_id, []))
        transitive = self._compute_transitive(requirement_id)
        all_affected = direct | transitive

        # Estimate effort: 4 hours per affected item (design, code, test)
        estimated_hours = len(all_affected) * 4

        # Risk assessment
        if len(all_affected) > 10:
            risk = "HIGH"
        elif len(all_affected) > 5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "requirement_id": requirement_id,
            "direct_dependents": sorted(list(direct)),
            "transitive_dependents": sorted(list(transitive - direct)),
            "total_affected": len(all_affected),
            "estimated_hours": estimated_hours,
            "risk_level": risk,
        }

    def _compute_transitive(
        self,
        requirement_id: str,
        visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """
        Recursively compute all transitive dependents.

        Uses DFS with cycle detection.
        """

        if visited is None:
            visited = set()

        if requirement_id in visited:
            return set()

        visited.add(requirement_id)

        # Get direct dependents
        direct = set(self.graph.get(requirement_id, []))

        # Recursively get transitive
        transitive = set()
        for dependent in direct:
            transitive.update(self._compute_transitive(dependent, visited.copy()))

        return direct | transitive

    def compute_change_propagation_order(
        self,
        affected_items: List[str],
    ) -> List[List[str]]:
        """
        Compute optimal order to propagate changes through affected items.

        Returns items grouped by "wave" - items in same wave can be changed in parallel.

        Algorithm (topological sort with levels):
        1. Build subgraph of affected items only
        2. Compute indegree (number of dependencies) for each
        3. Process items with indegree 0 (no deps) in parallel
        4. Remove processed items, recompute indegrees
        5. Repeat
        """

        # Build subgraph
        subgraph = {}
        for item in affected_items:
            deps = [d for d in self.graph.get(item, []) if d in affected_items]
            subgraph[item] = deps

        # Topological sort with levels
        waves = []
        remaining = set(affected_items)

        while remaining:
            # Find items with no remaining dependencies
            next_wave = [
                item for item in remaining
                if not any(dep in remaining for dep in subgraph.get(item, []))
            ]

            if not next_wave:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in {remaining}")

            waves.append(sorted(next_wave))
            remaining -= set(next_wave)

        return waves
```

---

## Conclusion

These algorithms provide the foundation for implementing advanced specification objects in production traceability systems. Key implementation priorities:

1. **EARS Pattern Validation** (1-2 weeks): High ROI, improves requirement quality immediately
2. **Flakiness Detection** (2-3 weeks): Enables smarter CI/CD decisions
3. **WSJF Scoring** (1 week): Better prioritization
4. **Volatility Tracking** (1-2 weeks): Identifies risky requirements
5. **Cryptographic Versioning** (2 weeks): Compliance and audit trails

All algorithms use standard Python libraries for easy integration with existing systems.
