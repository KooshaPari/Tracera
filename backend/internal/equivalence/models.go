// Package equivalence provides multi-dimensional traceability equivalence detection.
// It implements the Three-Layer Equivalence Model:
// 1. Canonical Concepts (abstract, view-agnostic entities)
// 2. View Projections (perspective-specific manifestations)
// 3. Inferred Equivalence (detected relationships)
package equivalence

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// StrategyType identifies the equivalence detection strategy used.
type StrategyType string

const (
	// Strategy confidence levels
	strategyConfidenceExplicit = 1.0
	strategyConfidenceHigh     = 0.9
	strategyConfidenceMedium   = 0.7
	strategyConfidenceLow      = 0.6
	strategyConfidenceFallback = 0.5
)

const (
	// StrategyExplicitAnnotation is a direct annotation (confidence 1.0).
	StrategyExplicitAnnotation StrategyType = "explicit_annotation"
	// StrategyManualLink is a user-created link (confidence 1.0).
	StrategyManualLink StrategyType = "manual_link"
	// StrategyAPIContract is a frontend → backend contract (confidence 0.9).
	StrategyAPIContract StrategyType = "api_contract"
	// StrategySharedCanonical indicates a shared canonical concept (confidence 0.9).
	StrategySharedCanonical StrategyType = "shared_canonical"
	// StrategyNamingPattern uses name similarity (confidence 0.7).
	StrategyNamingPattern StrategyType = "naming_pattern"
	// StrategySemanticSimilarity uses embeddings (confidence 0.6).
	StrategySemanticSimilarity StrategyType = "semantic_similarity"
	// StrategyStructural uses code structure (confidence 0.5).
	StrategyStructural StrategyType = "structural"
)

// DefaultConfidence returns the default confidence score for a strategy
func (s StrategyType) DefaultConfidence() float64 {
	switch s {
	case StrategyExplicitAnnotation, StrategyManualLink:
		return strategyConfidenceExplicit
	case StrategyAPIContract, StrategySharedCanonical:
		return strategyConfidenceHigh
	case StrategyNamingPattern:
		return strategyConfidenceMedium
	case StrategySemanticSimilarity:
		return strategyConfidenceLow
	case StrategyStructural:
		return strategyConfidenceFallback
	default:
		return strategyConfidenceFallback
	}
}

// Status represents the confirmation status of an equivalence.
type Status string

const (
	// StatusSuggested is AI-detected, awaiting confirmation.
	StatusSuggested Status = "suggested"
	// StatusConfirmed is user confirmed.
	StatusConfirmed Status = "confirmed"
	// StatusRejected is user rejected.
	StatusRejected Status = "rejected"
	// StatusAuto is auto-confirmed (high confidence).
	StatusAuto Status = "auto"
)

// CanonicalConcept represents an abstract, view-agnostic entity
type CanonicalConcept struct {
	ID                 uuid.UUID    `json:"id"`
	ProjectID          uuid.UUID    `json:"project_id"`
	Name               string       `json:"name"`
	Slug               string       `json:"slug"`
	Description        string       `json:"description,omitempty"`
	Domain             string       `json:"domain,omitempty"`
	Category           string       `json:"category,omitempty"`
	Tags               []string     `json:"tags"`
	Embedding          []float32    `json:"embedding,omitempty"`
	EmbeddingModel     string       `json:"embedding_model,omitempty"`
	EmbeddingUpdatedAt *time.Time   `json:"embedding_updated_at,omitempty"`
	ProjectionCount    int          `json:"projection_count"`
	RelatedConceptIDs  []uuid.UUID  `json:"related_concept_i_ds"`
	ParentConceptID    *uuid.UUID   `json:"parent_concept_id,omitempty"`
	ChildConceptIDs    []uuid.UUID  `json:"child_concept_i_ds"`
	Confidence         float64      `json:"confidence"`
	Source             StrategyType `json:"source"`
	CreatedBy          *uuid.UUID   `json:"created_by,omitempty"`
	CreatedAt          time.Time    `json:"created_at"`
	UpdatedAt          time.Time    `json:"updated_at"`
	Version            int          `json:"version"`
}

type canonicalConceptJSON struct {
	ID                 uuid.UUID    `json:"id"`
	ProjectID          uuid.UUID    `json:"project_id"`
	Name               string       `json:"name"`
	Slug               string       `json:"slug"`
	Description        string       `json:"description,omitempty"`
	Domain             string       `json:"domain,omitempty"`
	Category           string       `json:"category,omitempty"`
	Tags               []string     `json:"tags"`
	Embedding          []float32    `json:"embedding,omitempty"`
	EmbeddingModel     string       `json:"embedding_model,omitempty"`
	EmbeddingUpdatedAt *time.Time   `json:"embedding_updated_at,omitempty"`
	ProjectionCount    int          `json:"projection_count"`
	RelatedConceptIDs  []uuid.UUID  `json:"related_concept_i_ds"`
	ParentConceptID    *uuid.UUID   `json:"parent_concept_id,omitempty"`
	ChildConceptIDs    []uuid.UUID  `json:"child_concept_i_ds"`
	Confidence         float64      `json:"confidence"`
	Source             StrategyType `json:"source"`
	CreatedBy          *uuid.UUID   `json:"created_by,omitempty"`
	CreatedAt          time.Time    `json:"created_at"`
	UpdatedAt          time.Time    `json:"updated_at"`
	Version            int          `json:"version"`
}

// MarshalJSON writes canonical field names for compatibility.
func (c CanonicalConcept) MarshalJSON() ([]byte, error) {
	raw, err := json.Marshal(canonicalConceptJSON(c))
	if err != nil {
		return nil, err
	}

	var payload map[string]json.RawMessage
	if err := json.Unmarshal(raw, &payload); err != nil {
		return nil, err
	}

	if value, ok := payload["related_concept_i_ds"]; ok {
		payload["related_concept_ids"] = value
		delete(payload, "related_concept_i_ds")
	}

	if value, ok := payload["child_concept_i_ds"]; ok {
		payload["child_concept_ids"] = value
		delete(payload, "child_concept_i_ds")
	}

	return json.Marshal(payload)
}

// UnmarshalJSON accepts both canonical and tagliatelle field names.
func (concept *CanonicalConcept) UnmarshalJSON(data []byte) error {
	var payload map[string]json.RawMessage
	if err := json.Unmarshal(data, &payload); err != nil {
		return err
	}

	if value, ok := payload["related_concept_ids"]; ok {
		if _, exists := payload["related_concept_i_ds"]; !exists {
			payload["related_concept_i_ds"] = value
		}
	}

	if value, ok := payload["child_concept_ids"]; ok {
		if _, exists := payload["child_concept_i_ds"]; !exists {
			payload["child_concept_i_ds"] = value
		}
	}

	rewritten, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	var aux canonicalConceptJSON
	if err := json.Unmarshal(rewritten, &aux); err != nil {
		return err
	}

	*concept = CanonicalConcept(aux)
	return nil
}

// CanonicalProjection links a canonical concept to an item in a specific perspective
type CanonicalProjection struct {
	ID          uuid.UUID      `json:"id"`
	ProjectID   uuid.UUID      `json:"project_id"`
	CanonicalID uuid.UUID      `json:"canonical_id"`
	ItemID      uuid.UUID      `json:"item_id"`
	Perspective string         `json:"perspective"`
	Role        string         `json:"role,omitempty"` // primary, related, derived
	Confidence  float64        `json:"confidence"`
	Provenance  StrategyType   `json:"provenance"`
	Status      Status         `json:"status"`
	ConfirmedBy *uuid.UUID     `json:"confirmed_by,omitempty"`
	ConfirmedAt *time.Time     `json:"confirmed_at,omitempty"`
	Metadata    map[string]any `json:"metadata,omitempty"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
}

// Link represents a detected equivalence between two items.
type Link struct {
	ID           uuid.UUID    `json:"id"`
	ProjectID    uuid.UUID    `json:"project_id"`
	SourceItemID uuid.UUID    `json:"source_item_id"`
	TargetItemID uuid.UUID    `json:"target_item_id"`
	CanonicalID  *uuid.UUID   `json:"canonical_id,omitempty"`
	LinkType     string       `json:"link_type"` // same_as, represents, manifests_as, etc.
	Confidence   float64      `json:"confidence"`
	Provenance   StrategyType `json:"provenance"`
	Status       Status       `json:"status"`
	Evidence     []Evidence   `json:"evidence"`
	ConfirmedBy  *uuid.UUID   `json:"confirmed_by,omitempty"`
	ConfirmedAt  *time.Time   `json:"confirmed_at,omitempty"`
	CreatedAt    time.Time    `json:"created_at"`
	UpdatedAt    time.Time    `json:"updated_at"`
}

// Evidence represents supporting evidence for an equivalence detection.
type Evidence struct {
	Strategy    StrategyType   `json:"strategy"`
	Confidence  float64        `json:"confidence"`
	Description string         `json:"description"`
	Details     map[string]any `json:"details,omitempty"`
	DetectedAt  time.Time      `json:"detected_at"`
}

// Suggestion represents a suggested equivalence for user review.
type Suggestion struct {
	ID              uuid.UUID      `json:"id"`
	ProjectID       uuid.UUID      `json:"project_id"`
	SourceItemID    uuid.UUID      `json:"source_item_id"`
	SourceItemTitle string         `json:"source_item_title"`
	SourceItemType  string         `json:"source_item_type"`
	TargetItemID    uuid.UUID      `json:"target_item_id"`
	TargetItemTitle string         `json:"target_item_title"`
	TargetItemType  string         `json:"target_item_type"`
	SuggestedType   string         `json:"suggested_type"` // same_as, represents, etc.
	Confidence      float64        `json:"confidence"`
	Strategies      []StrategyType `json:"strategies"`
	Evidence        []Evidence     `json:"evidence"`
	CreatedAt       time.Time      `json:"created_at"`
}
