package docindex

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
)

const (
	conceptMatchIndexMin         = 4
	conceptMatchIndexAltMin      = 6
	conceptContextWindowPrimary  = 50
	conceptContextWindowFallback = 40
	conceptConfidencePrimary     = 0.8
	conceptConfidenceFallback    = 0.6
	conceptPhraseMinLength       = 3
	conceptProximityThreshold    = 200
)

// ConceptExtractor extracts and identifies business concepts from documentation
type ConceptExtractor struct {
	businessTerms map[string]ConceptType
	patterns      map[string]*regexp.Regexp
}

// ConceptType represents the classification of a business concept
type ConceptType string

const (
	// ConceptTypeFeature represents a feature-level concept.
	ConceptTypeFeature ConceptType = "feature"
	// ConceptTypeCapability represents a capability-level concept.
	ConceptTypeCapability ConceptType = "capability"
	// ConceptTypeDomain represents a domain-level concept.
	ConceptTypeDomain ConceptType = "domain"
	// ConceptTypeComponent represents a component-level concept.
	ConceptTypeComponent ConceptType = "component"
	// ConceptTypeRequirement represents a requirement-level concept.
	ConceptTypeRequirement ConceptType = "requirement"
	// ConceptTypeWorkflow represents a workflow-level concept.
	ConceptTypeWorkflow ConceptType = "workflow"
	// ConceptTypeEntity represents an entity-level concept.
	ConceptTypeEntity ConceptType = "entity"
	// ConceptTypeRule represents a rule-level concept.
	ConceptTypeRule ConceptType = "rule"
	// ConceptTypeIntegration represents an integration-level concept.
	ConceptTypeIntegration ConceptType = "integration"
	// ConceptTypeSystem represents a system-level concept.
	ConceptTypeSystem ConceptType = "system"
)

// ConceptMention represents a mention of a business concept in documentation
type ConceptMention struct {
	ID              uuid.UUID   `json:"id"`
	ProjectID       uuid.UUID   `json:"project_id"`
	DocEntityID     uuid.UUID   `json:"doc_entity_id"`
	ConceptType     ConceptType `json:"concept_type"`
	ConceptName     string      `json:"concept_name"`
	CanonicalForm   string      `json:"canonical_form"` // Normalized name for linking
	StartOffset     int         `json:"start_offset"`
	EndOffset       int         `json:"end_offset"`
	Context         string      `json:"context"`    // Surrounding text
	Confidence      float64     `json:"confidence"` // 0.0-1.0
	RelatedConcepts []string    `json:"related_concepts,omitempty"`
	CreatedAt       time.Time   `json:"created_at"`
}

// ConceptCluster represents a group of related concepts
type ConceptCluster struct {
	ID          uuid.UUID   `json:"id"`
	ProjectID   uuid.UUID   `json:"project_id"`
	Name        string      `json:"name"`
	Description string      `json:"description,omitempty"`
	Concepts    []string    `json:"concepts"`
	Type        ConceptType `json:"type"`
	CreatedAt   time.Time   `json:"created_at"`
	UpdatedAt   time.Time   `json:"updated_at"`
}

// BusinessTerm represents a known business term in the project
type BusinessTerm struct {
	ID              uuid.UUID   `json:"id"`
	ProjectID       uuid.UUID   `json:"project_id"`
	Term            string      `json:"term"`
	CanonicalForm   string      `json:"canonical_form"`
	Aliases         []string    `json:"aliases,omitempty"`
	ConceptType     ConceptType `json:"concept_type"`
	Definition      string      `json:"definition,omitempty"`
	RelatedTerms    []string    `json:"related_terms,omitempty"`
	Frequency       int         `json:"frequency"`
	LastMentionedAt time.Time   `json:"last_mentioned_at"`
	CreatedAt       time.Time   `json:"created_at"`
	UpdatedAt       time.Time   `json:"updated_at"`
}

// NewConceptExtractor creates a new concept extractor
func NewConceptExtractor() *ConceptExtractor {
	ce := &ConceptExtractor{
		businessTerms: make(map[string]ConceptType),
		patterns:      make(map[string]*regexp.Regexp),
	}
	ce.initializePatterns()
	return ce
}

// initializePatterns initializes regex patterns for concept detection
func (ce *ConceptExtractor) initializePatterns() {
	// Feature/capability patterns
	ce.patterns["feature"] = regexp.MustCompile(`(?i)(feature|capability|functionality|ability|feature:)[\s:]*([A-Z][a-z\s]+)`)

	// Workflow patterns
	ce.patterns["workflow"] = regexp.MustCompile(`(?i)(workflow|process|flow|procedure|steps|steps:)[\s:]*([A-Z][a-z\s]+)`)

	// Entity/model patterns
	ce.patterns["entity"] = regexp.MustCompile(`(?i)(entity|model|object|resource|type)[\s:]*([A-Z][a-zA-Z]+)`)

	// Rule/constraint patterns
	ce.patterns["rule"] = regexp.MustCompile(`(?i)(rule|constraint|requirement|must|should|restriction)[\s:]*([^\n.]+)`)

	// Integration patterns
	ce.patterns["integration"] = regexp.MustCompile(`(?i)(integration|api|interface|service|endpoint)[\s:]*([A-Z][a-zA-Z0-9\s]+)`)

	// Domain patterns
	ce.patterns["domain"] = regexp.MustCompile(`(?i)(domain|subdomain|area|scope)[\s:]*([A-Z][a-z\s]+)`)

	// Component patterns
	ce.patterns["component"] = regexp.MustCompile(`(?i)(component|module|package|library)[\s:]*([A-Za-z0-9_\-]+)`)
}

// extractPatternMentions extracts concept mentions from regex pattern matches.
func (ce *ConceptExtractor) extractPatternMentions(projectID uuid.UUID, docEntityID uuid.UUID, content string) []ConceptMention {
	var mentions []ConceptMention
	for conceptType, pattern := range ce.patterns {
		matches := pattern.FindAllStringSubmatchIndex(content, -1)
		for _, match := range matches {
			if len(match) < conceptMatchIndexMin {
				continue
			}
			conceptName := strings.TrimSpace(content[match[2]:match[3]])
			if conceptName == "" && len(match) >= conceptMatchIndexAltMin {
				conceptName = strings.TrimSpace(content[match[4]:match[5]])
			}
			if conceptName != "" {
				mentions = append(mentions, ConceptMention{
					ID:            uuid.New(),
					ProjectID:     projectID,
					DocEntityID:   docEntityID,
					ConceptType:   ConceptType(conceptType),
					ConceptName:   conceptName,
					CanonicalForm: normalizeConceptName(conceptName),
					StartOffset:   match[0],
					EndOffset:     match[1],
					Context:       extractContext(content, match[0], match[1], conceptContextWindowPrimary),
					Confidence:    conceptConfidencePrimary,
					CreatedAt:     time.Now(),
				})
			}
		}
	}
	return mentions
}

// extractNounPhraseMentions extracts capital-case noun phrases as potential entity concepts.
func extractNounPhraseMentions(projectID uuid.UUID, docEntityID uuid.UUID, content string) []ConceptMention {
	var mentions []ConceptMention
	nounPhrasePattern := regexp.MustCompile(`\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b`)
	matches := nounPhrasePattern.FindAllStringSubmatchIndex(content, -1)
	for _, match := range matches {
		phrase := content[match[0]:match[1]]
		if !isCommonNoun(phrase) && len(phrase) > conceptPhraseMinLength {
			mentions = append(mentions, ConceptMention{
				ID:            uuid.New(),
				ProjectID:     projectID,
				DocEntityID:   docEntityID,
				ConceptType:   ConceptTypeEntity,
				ConceptName:   phrase,
				CanonicalForm: normalizeConceptName(phrase),
				StartOffset:   match[0],
				EndOffset:     match[1],
				Context:       extractContext(content, match[0], match[1], conceptContextWindowFallback),
				Confidence:    conceptConfidenceFallback,
				CreatedAt:     time.Now(),
			})
		}
	}
	return mentions
}

// ExtractConcepts extracts concepts from documentation content
func (ce *ConceptExtractor) ExtractConcepts(projectID uuid.UUID, docEntityID uuid.UUID, content string) []ConceptMention {
	mentions := ce.extractPatternMentions(projectID, docEntityID, content)
	mentions = append(mentions, extractNounPhraseMentions(projectID, docEntityID, content)...)
	return mentions
}

// DetectRelationships detects relationships between concepts
func (ce *ConceptExtractor) DetectRelationships(mentions []ConceptMention) map[string][]string {
	relationships := make(map[string][]string)

	// Simple co-occurrence based relationships
	for i := 0; i < len(mentions); i++ {
		for j := i + 1; j < len(mentions); j++ {
			m1 := mentions[i]
			m2 := mentions[j]

			// If concepts appear close together, they're likely related
			if abs(m1.EndOffset-m2.StartOffset) < conceptProximityThreshold ||
				abs(m2.EndOffset-m1.StartOffset) < conceptProximityThreshold {
				relationships[m1.ConceptName] = append(relationships[m1.ConceptName], m2.ConceptName)
				relationships[m2.ConceptName] = append(relationships[m2.ConceptName], m1.ConceptName)
			}
		}
	}

	// Deduplicate
	for key, v := range relationships {
		seen := make(map[string]bool)
		dedup := []string{}
		for _, val := range v {
			if !seen[val] {
				dedup = append(dedup, val)
				seen[val] = true
			}
		}
		relationships[key] = dedup
	}

	return relationships
}

// AggregateConceptFrequency aggregates concept frequencies across a project
func (ce *ConceptExtractor) AggregateConceptFrequency(mentions []ConceptMention) map[string]int {
	frequency := make(map[string]int)
	for _, mention := range mentions {
		frequency[mention.CanonicalForm]++
	}
	return frequency
}

// LinkConceptsToConcepts creates business term records from extracted concepts
func (ce *ConceptExtractor) LinkConceptsToConcepts(projectID uuid.UUID, mentions []ConceptMention) []BusinessTerm {
	freqMap := make(map[string]int)
	conceptMap := make(map[string]ConceptMention)

	for _, m := range mentions {
		freqMap[m.CanonicalForm]++
		if _, exists := conceptMap[m.CanonicalForm]; !exists {
			conceptMap[m.CanonicalForm] = m
		}
	}

	terms := make([]BusinessTerm, 0, len(freqMap))
	for canonical, freq := range freqMap {
		mention := conceptMap[canonical]
		term := BusinessTerm{
			ID:              uuid.New(),
			ProjectID:       projectID,
			Term:            mention.ConceptName,
			CanonicalForm:   canonical,
			ConceptType:     mention.ConceptType,
			Frequency:       freq,
			LastMentionedAt: time.Now(),
			CreatedAt:       time.Now(),
			UpdatedAt:       time.Now(),
		}
		terms = append(terms, term)
	}

	return terms
}

// ConceptRepository defines repository operations for concepts.
type ConceptRepository interface {
	// SaveConceptMention saves a concept mention
	SaveConceptMention(ctx context.Context, mention *ConceptMention) error

	// GetConceptMentions retrieves concept mentions for a document entity
	GetConceptMentions(ctx context.Context, docEntityID uuid.UUID) ([]ConceptMention, error)

	// SaveBusinessTerm saves a business term
	SaveBusinessTerm(ctx context.Context, term *BusinessTerm) error

	// GetBusinessTerms retrieves business terms for a project
	GetBusinessTerms(ctx context.Context, projectID uuid.UUID) ([]BusinessTerm, error)

	// UpdateBusinessTermFrequency updates a business term's frequency
	UpdateBusinessTermFrequency(ctx context.Context, termID uuid.UUID, frequency int) error

	// SaveConceptCluster saves a concept cluster
	SaveConceptCluster(ctx context.Context, cluster *ConceptCluster) error

	// GetConceptClusters retrieves concept clusters for a project
	GetConceptClusters(ctx context.Context, projectID uuid.UUID) ([]ConceptCluster, error)

	// FindConceptsByType retrieves concepts by type
	FindConceptsByType(ctx context.Context, projectID uuid.UUID, conceptType ConceptType) ([]BusinessTerm, error)

	// DeleteConceptMentionsForEntity deletes concept mentions for a document entity
	DeleteConceptMentionsForEntity(ctx context.Context, docEntityID uuid.UUID) error
}

// Helper functions

// normalizeConceptName normalizes a concept name for canonical comparison
func normalizeConceptName(name string) string {
	return strings.ToLower(strings.TrimSpace(name))
}

// extractContext extracts surrounding context for a mention
func extractContext(content string, start, end, contextSize int) string {
	startIdx := start - contextSize
	if startIdx < 0 {
		startIdx = 0
	}

	endIdx := end + contextSize
	if endIdx > len(content) {
		endIdx = len(content)
	}

	return strings.TrimSpace(content[startIdx:endIdx])
}

// isCommonNoun checks if a phrase is a common noun
func isCommonNoun(phrase string) bool {
	common := map[string]bool{
		"The":         true,
		"And":         true,
		"Or":          true,
		"But":         true,
		"For":         true,
		"With":        true,
		"In":          true,
		"On":          true,
		"At":          true,
		"To":          true,
		"From":        true,
		"By":          true,
		"As":          true,
		"If":          true,
		"That":        true,
		"This":        true,
		"These":       true,
		"Those":       true,
		"Which":       true,
		"Who":         true,
		"Whom":        true,
		"Where":       true,
		"When":        true,
		"Why":         true,
		"How":         true,
		"Note":        true,
		"Warning":     true,
		"Error":       true,
		"Info":        true,
		"Debug":       true,
		"True":        true,
		"False":       true,
		"None":        true,
		"Null":        true,
		"Example":     true,
		"Description": true,
		"Returns":     true,
		"Parameters":  true,
		"Arguments":   true,
		"Page":        true,
		"Section":     true,
		"Chapter":     true,
		"Header":      true,
		"Footer":      true,
	}
	return common[phrase]
}

// abs returns absolute value
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}
