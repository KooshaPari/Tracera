package export

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// FormatVersion defines the current export format version for compatibility
const FormatVersion = "1.0.0"

// Format represents the target export format.
type Format string

const (
	// FormatJSON exports data as JSON.
	FormatJSON Format = "json"
	// FormatYAML exports data as YAML.
	FormatYAML Format = "yaml"
)

// Data represents the complete equivalence data export.
type Data struct {
	// Version tracks schema version for forward/backward compatibility
	Version string `json:"version" yaml:"version"`

	// ExportedAt is when the export was created
	ExportedAt time.Time `json:"exported_at" yaml:"exported_at"`

	// ProjectID is the project this data is from
	ProjectID uuid.UUID `json:"project_id" yaml:"project_id"`

	// ProjectName provides human-readable context
	ProjectName string `json:"project_name,omitempty" yaml:"project_name,omitempty"`

	// Metadata contains export-level metadata
	Metadata Metadata `json:"metadata" yaml:"metadata"`

	// CanonicalConcepts are the abstract concepts
	CanonicalConcepts []CanonicalConcept `json:"canonical_concepts" yaml:"canonical_concepts"`

	// Projections link concepts to specific items
	Projections []CanonicalProjection `json:"projections" yaml:"projections"`

	// EquivalenceLinks define relationships between items
	EquivalenceLinks []EquivalenceLink `json:"equivalence_links" yaml:"equivalence_links"`

	// Statistics about the export
	Statistics Statistics `json:"statistics" yaml:"statistics"`
}

// Metadata contains metadata about the export.
type Metadata struct {
	// ExportedBy identifies who initiated the export
	ExportedBy *uuid.UUID `json:"exported_by,omitempty" yaml:"exported_by,omitempty"`

	// Description provides context about this export
	Description string `json:"description,omitempty" yaml:"description,omitempty"`

	// Tags allow categorizing exports
	Tags []string `json:"tags,omitempty" yaml:"tags,omitempty"`

	// IncludeEmbeddings indicates if embeddings are included
	IncludeEmbeddings bool `json:"include_embeddings" yaml:"include_embeddings"`

	// IncludeMetadata indicates if item metadata is included
	IncludeMetadata bool `json:"include_metadata" yaml:"include_metadata"`

	// FilterCriteria describes what was filtered
	FilterCriteria map[string]interface{} `json:"filter_criteria,omitempty" yaml:"filter_criteria,omitempty"`
}

// CanonicalConcept represents a canonical concept in export format.
type CanonicalConcept struct {
	ID                uuid.UUID   `json:"id" yaml:"id"`
	ProjectID         uuid.UUID   `json:"project_id" yaml:"project_id"`
	Name              string      `json:"name" yaml:"name"`
	Slug              string      `json:"slug" yaml:"slug"`
	Description       string      `json:"description,omitempty" yaml:"description,omitempty"`
	Domain            string      `json:"domain,omitempty" yaml:"domain,omitempty"`
	Category          string      `json:"category,omitempty" yaml:"category,omitempty"`
	Tags              []string    `json:"tags,omitempty" yaml:"tags,omitempty"`
	Embedding         []float32   `json:"embedding,omitempty" yaml:"embedding,omitempty"`
	EmbeddingModel    string      `json:"embedding_model,omitempty" yaml:"embedding_model,omitempty"`
	ParentConceptID   *uuid.UUID  `json:"parent_concept_id,omitempty" yaml:"parent_concept_id,omitempty"`
	RelatedConceptIDs []uuid.UUID `json:"related_concept_i_ds,omitempty" yaml:"related_concept_ids,omitempty"`
	ProjectionCount   int         `json:"projection_count" yaml:"projection_count"`
	Confidence        float64     `json:"confidence" yaml:"confidence"`
	Source            string      `json:"source" yaml:"source"`
	CreatedBy         *uuid.UUID  `json:"created_by,omitempty" yaml:"created_by,omitempty"`
	CreatedAt         time.Time   `json:"created_at" yaml:"created_at"`
	UpdatedAt         time.Time   `json:"updated_at" yaml:"updated_at"`
	Version           int         `json:"version" yaml:"version"`
}

type canonicalConceptJSON struct {
	ID                uuid.UUID   `json:"id"`
	ProjectID         uuid.UUID   `json:"project_id"`
	Name              string      `json:"name"`
	Slug              string      `json:"slug"`
	Description       string      `json:"description,omitempty"`
	Domain            string      `json:"domain,omitempty"`
	Category          string      `json:"category,omitempty"`
	Tags              []string    `json:"tags,omitempty"`
	Embedding         []float32   `json:"embedding,omitempty"`
	EmbeddingModel    string      `json:"embedding_model,omitempty"`
	ParentConceptID   *uuid.UUID  `json:"parent_concept_id,omitempty"`
	RelatedConceptIDs []uuid.UUID `json:"related_concept_i_ds,omitempty"`
	ProjectionCount   int         `json:"projection_count"`
	Confidence        float64     `json:"confidence"`
	Source            string      `json:"source"`
	CreatedBy         *uuid.UUID  `json:"created_by,omitempty"`
	CreatedAt         time.Time   `json:"created_at"`
	UpdatedAt         time.Time   `json:"updated_at"`
	Version           int         `json:"version"`
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

// CanonicalProjection represents a projection in export format.
type CanonicalProjection struct {
	ID          uuid.UUID              `json:"id" yaml:"id"`
	ProjectID   uuid.UUID              `json:"project_id" yaml:"project_id"`
	CanonicalID uuid.UUID              `json:"canonical_id" yaml:"canonical_id"`
	ItemID      uuid.UUID              `json:"item_id" yaml:"item_id"`
	ItemTitle   string                 `json:"item_title,omitempty" yaml:"item_title,omitempty"`
	ItemType    string                 `json:"item_type,omitempty" yaml:"item_type,omitempty"`
	Perspective string                 `json:"perspective" yaml:"perspective"`
	Role        string                 `json:"role,omitempty" yaml:"role,omitempty"`
	Confidence  float64                `json:"confidence" yaml:"confidence"`
	Provenance  string                 `json:"provenance" yaml:"provenance"`
	Status      string                 `json:"status" yaml:"status"`
	ConfirmedBy *uuid.UUID             `json:"confirmed_by,omitempty" yaml:"confirmed_by,omitempty"`
	ConfirmedAt *time.Time             `json:"confirmed_at,omitempty" yaml:"confirmed_at,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty" yaml:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"created_at" yaml:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at" yaml:"updated_at"`
}

// EquivalenceLink represents an equivalence link in export format.
type EquivalenceLink struct {
	ID             uuid.UUID  `json:"id" yaml:"id"`
	ProjectID      uuid.UUID  `json:"project_id" yaml:"project_id"`
	SourceItemID   uuid.UUID  `json:"source_item_id" yaml:"source_item_id"`
	SourceItemInfo *ItemInfo  `json:"source_item_info,omitempty" yaml:"source_item_info,omitempty"`
	TargetItemID   uuid.UUID  `json:"target_item_id" yaml:"target_item_id"`
	TargetItemInfo *ItemInfo  `json:"target_item_info,omitempty" yaml:"target_item_info,omitempty"`
	CanonicalID    *uuid.UUID `json:"canonical_id,omitempty" yaml:"canonical_id,omitempty"`
	LinkType       string     `json:"link_type" yaml:"link_type"`
	Confidence     float64    `json:"confidence" yaml:"confidence"`
	Provenance     string     `json:"provenance" yaml:"provenance"`
	Status         string     `json:"status" yaml:"status"`
	Evidence       []Evidence `json:"evidence,omitempty" yaml:"evidence,omitempty"`
	ConfirmedBy    *uuid.UUID `json:"confirmed_by,omitempty" yaml:"confirmed_by,omitempty"`
	ConfirmedAt    *time.Time `json:"confirmed_at,omitempty" yaml:"confirmed_at,omitempty"`
	CreatedAt      time.Time  `json:"created_at" yaml:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" yaml:"updated_at"`
}

// Evidence represents evidence in export format.
type Evidence struct {
	Strategy    string                 `json:"strategy" yaml:"strategy"`
	Confidence  float64                `json:"confidence" yaml:"confidence"`
	Description string                 `json:"description" yaml:"description"`
	Details     map[string]interface{} `json:"details,omitempty" yaml:"details,omitempty"`
	DetectedAt  time.Time              `json:"detected_at" yaml:"detected_at"`
}

// ItemInfo contains minimal item information for context.
type ItemInfo struct {
	ID          uuid.UUID              `json:"id" yaml:"id"`
	Title       string                 `json:"title" yaml:"title"`
	Description string                 `json:"description,omitempty" yaml:"description,omitempty"`
	ItemType    string                 `json:"item_type" yaml:"item_type"`
	Status      string                 `json:"status,omitempty" yaml:"status,omitempty"`
	Priority    string                 `json:"priority,omitempty" yaml:"priority,omitempty"`
	Tags        []string               `json:"tags,omitempty" yaml:"tags,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty" yaml:"metadata,omitempty"`
}

// Statistics provides information about the export.
type Statistics struct {
	// CanonicalConceptCount is the number of canonical concepts
	CanonicalConceptCount int `json:"canonical_concept_count" yaml:"canonical_concept_count"`

	// ProjectionCount is the number of projections
	ProjectionCount int `json:"projection_count" yaml:"projection_count"`

	// EquivalenceLinkCount is the number of equivalence links
	EquivalenceLinkCount int `json:"equivalence_link_count" yaml:"equivalence_link_count"`

	// ConfirmedCount is the number of confirmed equivalences
	ConfirmedCount int `json:"confirmed_count" yaml:"confirmed_count"`

	// SuggestedCount is the number of suggested equivalences
	SuggestedCount int `json:"suggested_count" yaml:"suggested_count"`

	// RejectedCount is the number of rejected equivalences
	RejectedCount int `json:"rejected_count" yaml:"rejected_count"`

	// PerspectiveCount is the number of distinct perspectives
	PerspectiveCount int `json:"perspective_count" yaml:"perspective_count"`

	// AverageConfidence is the mean confidence across all links
	AverageConfidence float64 `json:"average_confidence" yaml:"average_confidence"`

	// StrategyBreakdown shows distribution by strategy
	StrategyBreakdown map[string]int `json:"strategy_breakdown" yaml:"strategy_breakdown"`

	// DomainBreakdown shows distribution by domain
	DomainBreakdown map[string]int `json:"domain_breakdown" yaml:"domain_breakdown"`
}
