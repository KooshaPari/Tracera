package equivalence

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// ============================================================================
// REQUEST TYPES
// ============================================================================

// DetectionRequest represents a request to detect equivalences
// POST /api/v1/equivalences/detect
type DetectionRequest struct {
	// ProjectID is the project to search for equivalences within
	ProjectID uuid.UUID `json:"project_id" binding:"required"`

	// SourceItemID is the item to find equivalences for
	SourceItemID uuid.UUID `json:"source_item_id" binding:"required"`

	// Strategies specifies which detection strategies to use
	// If empty, all strategies are used
	Strategies []StrategyType `json:"strategies,omitempty"`

	// MinConfidence filters suggestions below this threshold (0.0-1.0)
	MinConfidence float64 `json:"min_confidence,omitempty"`

	// MaxResults limits the number of suggestions returned
	MaxResults int `json:"max_results,omitempty"`

	// CandidatePool specifies which items to check (if nil, checks all items in project)
	CandidatePool []*ItemInfo `json:"candidate_pool,omitempty"`
}

// ListEquivalencesRequest represents a request to list equivalence links
// GET /api/v1/equivalences?project_id=X&status=confirmed&limit=50&offset=0
type ListEquivalencesRequest struct {
	// ProjectID filters equivalences to a specific project
	ProjectID uuid.UUID `json:"project_id" form:"project_id"`

	// Status filters by confirmation status (suggested, confirmed, rejected, auto)
	Status Status `json:"status" form:"status"`

	// MinConfidence filters links below this threshold
	MinConfidence float64 `json:"min_confidence" form:"min_confidence"`

	// LinkType filters by link type (same_as, represents, manifests_as, etc.)
	LinkType string `json:"link_type" form:"link_type"`

	// Limit is the maximum number of results to return (default: 50, max: 500)
	Limit int `json:"limit" form:"limit"`

	// Offset is the number of results to skip (default: 0)
	Offset int `json:"offset" form:"offset"`

	// SortBy specifies sort order (created_at, confidence, updated_at)
	SortBy string `json:"sort_by" form:"sort_by"`

	// SortDirection specifies sort direction (asc, desc)
	SortDirection string `json:"sort_direction" form:"sort_direction"`
}

// ConfirmEquivalenceRequest represents a request to confirm an equivalence
// POST /api/v1/equivalences/{id}/confirm
type ConfirmEquivalenceRequest struct {
	// Reason is optional context for the confirmation
	Reason string `json:"reason,omitempty"`

	// Metadata is optional additional information
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// RejectEquivalenceRequest represents a request to reject an equivalence
// POST /api/v1/equivalences/{id}/reject
type RejectEquivalenceRequest struct {
	// Reason explains why the equivalence was rejected
	Reason string `json:"reason,omitempty"`

	// Metadata is optional additional information
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// BulkConfirmRequest represents a request to confirm multiple equivalences
// POST /api/v1/equivalences/bulk-confirm
type BulkConfirmRequest struct {
	// EquivalenceIDs are the IDs to confirm
	EquivalenceIDs []uuid.UUID `json:"equivalence_i_ds" binding:"required"`

	// Reason is optional context for all confirmations
	Reason string `json:"reason,omitempty"`
}

// BulkRejectRequest represents a request to reject multiple equivalences
// POST /api/v1/equivalences/bulk-reject
type BulkRejectRequest struct {
	// EquivalenceIDs are the IDs to reject
	EquivalenceIDs []uuid.UUID `json:"equivalence_i_ds" binding:"required"`

	// Reason explains why equivalences were rejected
	Reason string `json:"reason,omitempty"`
}

// GetCanonicalConceptsRequest represents filtering options for canonical concepts
// GET /api/v1/canonical-concepts?project_id=X&domain=X&limit=50&offset=0
type GetCanonicalConceptsRequest struct {
	// ProjectID filters to a specific project
	ProjectID uuid.UUID `form:"project_id" binding:"required"`

	// Domain filters by domain classification
	Domain string `form:"domain"`

	// Category filters by category
	Category string `form:"category"`

	// ParentID filters to concepts under a parent
	ParentID *uuid.UUID `form:"parent_id"`

	// Tags filters to concepts with any of these tags
	Tags []string `form:"tags"`

	// SearchQuery performs text search on name and description
	SearchQuery string `form:"q"`

	// Limit is maximum results (default: 50, max: 500)
	Limit int `form:"limit"`

	// Offset for pagination
	Offset int `form:"offset"`

	// SortBy specifies sort field (name, created_at, projection_count)
	SortBy string `form:"sort_by"`
}

// CreateCanonicalConceptRequest represents a request to create a canonical concept
// POST /api/v1/canonical-concepts
type CreateCanonicalConceptRequest struct {
	// ProjectID is the owning project
	ProjectID uuid.UUID `json:"project_id" binding:"required"`

	// Name is the concept name
	Name string `json:"name" binding:"required"`

	// Description explains the concept
	Description string `json:"description"`

	// Domain is optional domain classification
	Domain string `json:"domain"`

	// Category is optional categorization
	Category string `json:"category"`

	// Tags are optional tags for organization
	Tags []string `json:"tags"`

	// ParentConceptID links to a parent concept (optional)
	ParentConceptID *uuid.UUID `json:"parent_concept_id"`

	// Metadata is optional additional data
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// MarshalJSON writes the canonical equivalence_ids field name for compatibility.
func (request BulkConfirmRequest) MarshalJSON() ([]byte, error) {
	payload := map[string]interface{}{
		"equivalence_ids": request.EquivalenceIDs,
	}
	if request.Reason != "" {
		payload["reason"] = request.Reason
	}
	return json.Marshal(payload)
}

// UnmarshalJSON accepts both equivalence_ids and equivalence_i_ds.
func (request *BulkConfirmRequest) UnmarshalJSON(data []byte) error {
	payload, err := decodeBulkEquivalencePayload(data)
	if err != nil {
		return err
	}
	request.EquivalenceIDs = payload.equivalenceIDs
	request.Reason = payload.reason
	return nil
}

// MarshalJSON writes the canonical equivalence_ids field name for compatibility.
func (request BulkRejectRequest) MarshalJSON() ([]byte, error) {
	payload := map[string]interface{}{
		"equivalence_ids": request.EquivalenceIDs,
	}
	if request.Reason != "" {
		payload["reason"] = request.Reason
	}
	return json.Marshal(payload)
}

// UnmarshalJSON accepts both equivalence_ids and equivalence_i_ds.
func (request *BulkRejectRequest) UnmarshalJSON(data []byte) error {
	payload, err := decodeBulkEquivalencePayload(data)
	if err != nil {
		return err
	}
	request.EquivalenceIDs = payload.equivalenceIDs
	request.Reason = payload.reason
	return nil
}

type bulkEquivalencePayload struct {
	equivalenceIDs []uuid.UUID
	reason         string
}

func decodeBulkEquivalencePayload(data []byte) (bulkEquivalencePayload, error) {
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return bulkEquivalencePayload{}, err
	}

	equivalenceIDs, err := decodeEquivalenceIDs(raw)
	if err != nil {
		return bulkEquivalencePayload{}, err
	}

	reason, err := decodeBulkReason(raw)
	if err != nil {
		return bulkEquivalencePayload{}, err
	}

	return bulkEquivalencePayload{
		equivalenceIDs: equivalenceIDs,
		reason:         reason,
	}, nil
}

func decodeEquivalenceIDs(raw map[string]json.RawMessage) ([]uuid.UUID, error) {
	if rawIDs, ok := raw["equivalence_ids"]; ok {
		return decodeUUIDList(rawIDs)
	}
	if rawIDs, ok := raw["equivalence_i_ds"]; ok {
		return decodeUUIDList(rawIDs)
	}
	return nil, nil
}

func decodeBulkReason(raw map[string]json.RawMessage) (string, error) {
	rawReason, ok := raw["reason"]
	if !ok {
		return "", nil
	}

	var reason string
	if err := json.Unmarshal(rawReason, &reason); err != nil {
		return "", err
	}
	return reason, nil
}

func decodeUUIDList(rawList json.RawMessage) ([]uuid.UUID, error) {
	var ids []uuid.UUID
	if err := json.Unmarshal(rawList, &ids); err != nil {
		return nil, err
	}
	return ids, nil
}

// GetProjectionsRequest represents a request to get projections for a concept
// GET /api/v1/canonical-concepts/{id}/projections?perspective=X&limit=50
type GetProjectionsRequest struct {
	// ConceptID is the canonical concept
	ConceptID uuid.UUID `form:"concept_id"`

	// Perspective filters to a specific perspective
	Perspective string `form:"perspective"`

	// Status filters by status (suggested, confirmed, rejected)
	Status Status `form:"status"`

	// Limit is maximum results
	Limit int `form:"limit"`

	// Offset for pagination
	Offset int `form:"offset"`
}

// CreateCanonicalProjectionRequest represents a request to create a projection
// POST /api/v1/concepts/:id/projections
type CreateCanonicalProjectionRequest struct {
	// ItemID is the item being projected onto the canonical concept
	ItemID uuid.UUID `json:"item_id" binding:"required"`

	// Perspective is the view perspective (e.g., code, requirements, design)
	Perspective string `json:"perspective,omitempty"`

	// Role is the role of this projection (primary, related, derived)
	Role string `json:"role,omitempty"`

	// Confidence is the confidence of this projection (0.0-1.0)
	Confidence float64 `json:"confidence,omitempty"`

	// Source indicates how the projection was detected/confirmed
	Source StrategyType `json:"source,omitempty"`

	// Metadata is optional additional information
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// CreateCanonicalProjectionResponse is returned after creating a projection
// Response for: POST /api/v1/concepts/:id/projections
type CreateCanonicalProjectionResponse struct {
	// Projection is the created projection
	Projection CanonicalProjection `json:"projection"`

	// Message describes the creation
	Message string `json:"message"`

	// CreatedAt is when the projection was created
	CreatedAt time.Time `json:"created_at"`
}

// PivotNavigationRequest represents a request to get equivalent items for pivot navigation
// POST /api/v1/items/{id}/pivot
type PivotNavigationRequest struct {
	// ItemID is the item to pivot from
	ItemID uuid.UUID `json:"item_id"`

	// Perspectives specifies which perspectives to include (e.g., code, requirements, design)
	Perspectives []string `json:"perspectives,omitempty"`

	// MaxDepth limits transitive equivalence depth (default: 1)
	MaxDepth int `json:"max_depth,omitempty"`

	// IncludeMetadata includes full item metadata in results
	IncludeMetadata bool `json:"include_metadata,omitempty"`

	// GroupByPerspective organizes results by perspective
	GroupByPerspective bool `json:"group_by_perspective,omitempty"`
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

// ListEquivalencesResponse contains equivalence links with pagination
// Response for: GET /api/v1/equivalences
type ListEquivalencesResponse struct {
	// Data is the list of equivalence links
	Data []Link `json:"data"`

	// Total is the total number of records matching the filter
	Total int64 `json:"total"`

	// Limit is the limit used in the request
	Limit int `json:"limit"`

	// Offset is the offset used in the request
	Offset int `json:"offset"`

	// HasMore indicates if there are more results
	HasMore bool `json:"has_more"`
}

// DetectionResponse contains detection results
// Response for: POST /api/v1/equivalences/detect
type DetectionResponse struct {
	// Suggestions are the detected equivalence suggestions
	Suggestions []Suggestion `json:"suggestions"`

	// Stats contains detection statistics
	Stats DetectionStats `json:"stats"`

	// Timestamp when detection was performed
	DetectedAt time.Time `json:"detected_at"`
}

// DetectionStats contains statistics about detection run
type DetectionStats struct {
	// TotalItemsScanned is the number of items checked
	TotalItemsScanned int `json:"total_items_scanned"`

	// EquivalencesFound is the number of suggestions created
	EquivalencesFound int `json:"equivalences_found"`

	// AverageConfidence is the mean confidence across all findings
	AverageConfidence float64 `json:"average_confidence"`

	// StrategyBreakdown shows count by strategy
	StrategyBreakdown map[StrategyType]int `json:"strategy_breakdown"`

	// DurationMs is detection time in milliseconds
	DurationMs int64 `json:"duration_ms"`
}

// ConfirmEquivalenceResponse is the response after confirming an equivalence
// Response for: POST /api/v1/equivalences/{id}/confirm
type ConfirmEquivalenceResponse struct {
	// Link is the confirmed equivalence link
	Link Link `json:"link"`

	// Message describes the confirmation
	Message string `json:"message"`

	// ConfirmedAt is when confirmation occurred
	ConfirmedAt time.Time `json:"confirmed_at"`
}

// BulkConfirmResponse is the response for bulk confirmation
// Response for: POST /api/v1/equivalences/bulk-confirm
type BulkConfirmResponse struct {
	// Confirmed is the number of successfully confirmed links
	Confirmed int `json:"confirmed"`

	// Failed is the number that failed to confirm
	Failed int `json:"failed"`

	// Links are the confirmed equivalence links
	Links []Link `json:"links"`

	// Errors maps failed IDs to error messages
	Errors map[string]string `json:"errors,omitempty"`
}

// ListCanonicalConceptsResponse contains canonical concepts with pagination
// Response for: GET /api/v1/canonical-concepts
type ListCanonicalConceptsResponse struct {
	// Data is the list of canonical concepts
	Data []CanonicalConcept `json:"data"`

	// Total is the total number matching filters
	Total int64 `json:"total"`

	// Limit used in request
	Limit int `json:"limit"`

	// Offset used in request
	Offset int `json:"offset"`

	// HasMore indicates if more results exist
	HasMore bool `json:"has_more"`
}

// CreateCanonicalConceptResponse is returned when creating a canonical concept
// Response for: POST /api/v1/canonical-concepts
type CreateCanonicalConceptResponse struct {
	// Concept is the created canonical concept
	Concept CanonicalConcept `json:"concept"`

	// Message describes the creation
	Message string `json:"message"`

	// CreatedAt is when the concept was created
	CreatedAt time.Time `json:"created_at"`
}

// GetProjectionsResponse contains projections for a canonical concept
// Response for: GET /api/v1/canonical-concepts/{id}/projections
type GetProjectionsResponse struct {
	// ConceptID is the canonical concept
	ConceptID uuid.UUID `json:"concept_id"`

	// Concept is the canonical concept details
	Concept *CanonicalConcept `json:"concept,omitempty"`

	// Projections are the view manifestations
	Projections []CanonicalProjection `json:"projections"`

	// PerspectiveBreakdown groups projections by perspective
	PerspectiveBreakdown map[string][]CanonicalProjection `json:"perspective_breakdown,omitempty"`

	// Total number of projections
	Total int64 `json:"total"`
}

// PivotNavigationResponse contains equivalent items grouped by perspective
// Response for: POST /api/v1/items/{id}/pivot
type PivotNavigationResponse struct {
	// SourceItemID is the original item
	SourceItemID uuid.UUID `json:"source_item_id"`

	// SourceItem includes source item details
	SourceItem *ItemInfo `json:"source_item,omitempty"`

	// EquivalentsByPerspective groups equivalent items by perspective
	EquivalentsByPerspective map[string][]PivotItem `json:"equivalents_by_perspective"`

	// AllEquivalents is flat list of all equivalent items
	AllEquivalents []PivotItem `json:"all_equivalents"`

	// CanonicalConcept is the shared abstract concept (if applicable)
	CanonicalConcept *CanonicalConcept `json:"canonical_concept,omitempty"`

	// LinkCount is the number of equivalence relationships found
	LinkCount int `json:"link_count"`

	// PerspectiveCount is the number of perspectives represented
	PerspectiveCount int `json:"perspective_count"`
}

// PivotItem represents an equivalent item in pivot navigation
type PivotItem struct {
	// ItemID is the equivalent item
	ItemID uuid.UUID `json:"item_id"`

	// Title is the item title/name
	Title string `json:"title"`

	// ItemType is the item type (requirement, feature, etc.)
	ItemType string `json:"item_type"`

	// Perspective is the item's perspective (code, requirements, etc.)
	Perspective string `json:"perspective"`

	// LinkType is how it's equivalent (same_as, represents, manifests_as)
	LinkType string `json:"link_type"`

	// Confidence is the confidence of equivalence (0.0-1.0)
	Confidence float64 `json:"confidence"`

	// Status is the equivalence status
	Status Status `json:"status"`

	// Item includes full item details if requested
	Item *ItemInfo `json:"item,omitempty"`

	// RelatedCanonicalID if this projection links to a canonical concept
	RelatedCanonicalID *uuid.UUID `json:"related_canonical_id,omitempty"`

	// PathDepth is transitive depth from source (1 = direct, 2 = indirect)
	PathDepth int `json:"path_depth"`
}

// ItemInfo contains basic information about an item for embedding in responses
type ItemInfo struct {
	// ID is the item unique identifier
	ID uuid.UUID `json:"id"`

	// ProjectID is the owning project
	ProjectID uuid.UUID `json:"project_id"`

	// Title is the item title
	Title string `json:"title"`

	// Description is the item description
	Description string `json:"description,omitempty"`

	// ItemType is the item classification
	ItemType string `json:"item_type"`

	// Status is the item status
	Status string `json:"status"`

	// Priority is the item priority
	Priority string `json:"priority,omitempty"`

	// Metadata contains additional item data
	Metadata map[string]interface{} `json:"metadata,omitempty"`

	// CodeRef links to source code
	CodeRef *CodeReference `json:"code_ref,omitempty"`

	// Tags are item tags
	Tags []string `json:"tags,omitempty"`

	// CreatedAt is creation timestamp
	CreatedAt time.Time `json:"created_at"`

	// UpdatedAt is last modification timestamp
	UpdatedAt time.Time `json:"updated_at"`
}

// CodeReference represents a reference to source code
type CodeReference struct {
	// FilePath is the source file path
	FilePath string `json:"file_path"`

	// SymbolName is the symbol name
	SymbolName string `json:"symbol_name"`

	// SymbolType is the symbol type (function, class, method, etc.)
	SymbolType string `json:"symbol_type"`

	// LineStart is the starting line number
	LineStart int `json:"line_start"`

	// LineEnd is the ending line number
	LineEnd int `json:"line_end"`

	// Repository is the code repository
	Repository string `json:"repository,omitempty"`
}

// ErrorResponse is returned for errors
type ErrorResponse struct {
	// Error is the error message
	Error string `json:"error"`

	// Code is the error code
	Code string `json:"code,omitempty"`

	// Details contains additional error context
	Details map[string]interface{} `json:"details,omitempty"`

	// Timestamp when error occurred
	Timestamp time.Time `json:"timestamp"`
}

// ============================================================================
// BULK OPERATIONS RESPONSE
// ============================================================================

// BulkRejectResponse is returned after bulk rejection
// Response for: POST /api/v1/equivalences/bulk-reject
type BulkRejectResponse struct {
	// Rejected is the number of successfully rejected equivalences
	Rejected int `json:"rejected"`

	// Failed is the number that failed to reject
	Failed int `json:"failed"`

	// Errors maps failed IDs to error messages
	Errors map[string]string `json:"errors,omitempty"`
}

// ============================================================================
// FILTER & SORT HELPERS
// ============================================================================

// Filter encapsulates all filter options.
type Filter struct {
	// ProjectID is the project to filter by
	ProjectID uuid.UUID

	// Status is the confirmation status
	Status Status

	// MinConfidence is the minimum confidence threshold
	MinConfidence float64

	// LinkType is the equivalence type
	LinkType string

	// Strategy is the detection strategy
	Strategy StrategyType

	// SourceItemID filters to equivalences for this source
	SourceItemID *uuid.UUID

	// TargetItemID filters to equivalences for this target
	TargetItemID *uuid.UUID
}

// SortOptions specifies how to sort results
type SortOptions struct {
	// Field to sort by
	Field string

	// Direction of sort (asc or desc)
	Direction string
}

// PaginationOptions specifies pagination parameters
type PaginationOptions struct {
	// Limit is the page size
	Limit int

	// Offset is the number of items to skip
	Offset int
}
