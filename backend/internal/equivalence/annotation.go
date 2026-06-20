package equivalence

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
)

const annotationMatchMinCount = 2

// AnnotationStrategy detects equivalences from explicit code annotations
// Supports: @trace-implements, @canonical, @same-as, @relates-to
type AnnotationStrategy struct {
	patterns map[string]*regexp.Regexp
}

// NewAnnotationStrategy creates a new annotation parser strategy
func NewAnnotationStrategy() *AnnotationStrategy {
	return &AnnotationStrategy{
		patterns: map[string]*regexp.Regexp{
			"implements": regexp.MustCompile(`@trace-implements?\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
			"canonical":  regexp.MustCompile(`@canonical\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
			"same_as":    regexp.MustCompile(`@same-as\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
			"relates_to": regexp.MustCompile(`@relates-to\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
			"tests":      regexp.MustCompile(`@tests?\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
			"documents":  regexp.MustCompile(`@documents?\s*[:\(]?\s*["']?([^"'\)\s]+)["']?\)?`),
		},
	}
}

// Name returns the strategy identifier.
func (strategy *AnnotationStrategy) Name() StrategyType {
	return StrategyExplicitAnnotation
}

// DefaultConfidence returns the base confidence for annotations.
func (strategy *AnnotationStrategy) DefaultConfidence() float64 {
	return 1.0 // Explicit annotations are highest confidence
}

// RequiresEmbeddings reports whether this strategy needs embeddings.
func (strategy *AnnotationStrategy) RequiresEmbeddings() bool {
	return false
}

// Detect finds equivalences using explicit annotations.
func (strategy *AnnotationStrategy) Detect(
	ctx context.Context,
	req *StrategyDetectionRequest,
) (*DetectionResult, error) {
	start := time.Now()
	result := &DetectionResult{
		Strategy: strategy.Name(),
		Links:    make([]Link, 0),
	}

	// Extract annotations from source item
	annotations := strategy.extractAnnotations(req.SourceItem)
	if len(annotations) == 0 {
		result.DurationMs = time.Since(start).Milliseconds()
		return result, nil
	}

	// Build a lookup map from candidate pool
	candidateByName, candidateByID := strategy.indexCandidates(req, result)

	// Match annotations to candidates
	for _, annotation := range annotations {
		select {
		case <-ctx.Done():
			result.Error = ctx.Err().Error()
			return result, ctx.Err()
		default:
		}

		target := strategy.findTarget(annotation.Reference, candidateByName, candidateByID)
		if target == nil {
			continue
		}

		link := strategy.buildLink(req, annotation, target)
		result.Links = append(result.Links, link)
	}

	result.DurationMs = time.Since(start).Milliseconds()
	return result, nil
}

func (strategy *AnnotationStrategy) indexCandidates(
	req *StrategyDetectionRequest,
	result *DetectionResult,
) (map[string]*StrategyItemInfo, map[string]*StrategyItemInfo) {
	candidateByName := make(map[string]*StrategyItemInfo)
	candidateByID := make(map[string]*StrategyItemInfo)

	for _, candidate := range req.CandidatePool {
		result.ItemsScanned++
		if candidate.ID == req.SourceItem.ID {
			continue
		}

		candidateByName[strings.ToLower(candidate.Title)] = candidate
		candidateByID[candidate.ID.String()] = candidate
		if candidate.CodeRef != nil {
			candidateByName[strings.ToLower(candidate.CodeRef.SymbolName)] = candidate
		}
	}

	return candidateByName, candidateByID
}

func (strategy *AnnotationStrategy) buildLink(
	req *StrategyDetectionRequest,
	annotation Annotation,
	target *StrategyItemInfo,
) Link {
	now := time.Now()
	confidence := strategy.DefaultConfidence()

	return Link{
		ID:           uuid.New(),
		ProjectID:    req.ProjectID,
		SourceItemID: req.SourceItem.ID,
		TargetItemID: target.ID,
		LinkType:     annotation.Type,
		Confidence:   confidence,
		Provenance:   strategy.Name(),
		Status:       StatusAuto, // Auto-confirm explicit annotations
		Evidence: []Evidence{{
			Strategy:    strategy.Name(),
			Confidence:  confidence,
			Description: "Explicit annotation in source code",
			Details: map[string]any{
				"annotation_type": annotation.Type,
				"reference":       annotation.Reference,
				"raw":             annotation.Raw,
			},
			DetectedAt: now,
		}},
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// Annotation represents a parsed code annotation
type Annotation struct {
	Type      string // implements, canonical, same_as, etc.
	Reference string // The referenced entity (ID, name, or path)
	Raw       string // The raw annotation text
}

// extractAnnotations parses annotations from item metadata
func (strategy *AnnotationStrategy) extractAnnotations(item *StrategyItemInfo) []Annotation {
	metadataAnnotations := strategy.extractAnnotationsFromMetadata(item.Metadata)
	descriptionAnnotations := strategy.parseAnnotationsFromText(item.Description)
	annotations := make([]Annotation, 0, len(metadataAnnotations)+len(descriptionAnnotations))
	annotations = append(annotations, metadataAnnotations...)
	annotations = append(annotations, descriptionAnnotations...)
	return annotations
}

func (strategy *AnnotationStrategy) extractAnnotationsFromMetadata(metadata map[string]interface{}) []Annotation {
	if metadata == nil {
		return nil
	}

	annotations := extractAnnotationsFromMetadataList(metadata["annotations"])
	if comments, ok := metadata["comments"].(string); ok {
		annotations = append(annotations, strategy.parseAnnotationsFromText(comments)...)
	}

	return annotations
}

func extractAnnotationsFromMetadataList(rawAnnotations interface{}) []Annotation {
	annotationList, ok := rawAnnotations.([]interface{})
	if !ok {
		return nil
	}

	annotations := make([]Annotation, 0, len(annotationList))
	for _, rawAnnotation := range annotationList {
		if annotation, ok := parseAnnotationMap(rawAnnotation); ok {
			annotations = append(annotations, annotation)
		}
	}

	return annotations
}

func parseAnnotationMap(rawAnnotation interface{}) (Annotation, bool) {
	annotationMap, ok := rawAnnotation.(map[string]interface{})
	if !ok {
		return Annotation{}, false
	}

	annotationType, okType := annotationMap["type"].(string)
	reference, okReference := annotationMap["reference"].(string)
	raw, okRaw := annotationMap["raw"].(string)
	if !okType || !okReference || !okRaw {
		return Annotation{}, false
	}

	return Annotation{
		Type:      annotationType,
		Reference: reference,
		Raw:       raw,
	}, true
}

// parseAnnotationsFromText extracts annotations from free-form text
func (strategy *AnnotationStrategy) parseAnnotationsFromText(text string) []Annotation {
	var annotations []Annotation

	for annotType, pattern := range strategy.patterns {
		matches := pattern.FindAllStringSubmatch(text, -1)
		for _, match := range matches {
			if len(match) >= annotationMatchMinCount {
				annotations = append(annotations, Annotation{
					Type:      annotType,
					Reference: match[1],
					Raw:       match[0],
				})
			}
		}
	}

	return annotations
}

// findTarget finds a target item from a reference string
func (strategy *AnnotationStrategy) findTarget(
	ref string,
	byName map[string]*StrategyItemInfo,
	byID map[string]*StrategyItemInfo,
) *StrategyItemInfo {
	// Try exact ID match
	if target, ok := byID[ref]; ok {
		return target
	}

	// Try name match (case-insensitive)
	ref = strings.ToLower(ref)
	if target, ok := byName[ref]; ok {
		return target
	}

	// Try partial match on name
	for name, target := range byName {
		if strings.Contains(name, ref) || strings.Contains(ref, name) {
			return target
		}
	}

	return nil
}
