package docindex

import (
	"context"
	"strings"
	"time"

	"github.com/google/uuid"
)

const (
	docLinkSymbolConfidenceScale = 0.9
	docLinkAPIConfidence         = 0.85
)

// Linker creates traceability links between documentation and code entities
type Linker struct {
	docRepo  Repository
	codeRepo CodeEntityRepository
}

// CodeEntityRepository defines the interface for code entity storage
type CodeEntityRepository interface {
	FindByFilePath(ctx context.Context, projectID uuid.UUID, filePath string) ([]CodeEntity, error)
	FindBySymbolName(ctx context.Context, projectID uuid.UUID, name string) ([]CodeEntity, error)
	SearchByEmbedding(ctx context.Context, projectID uuid.UUID, embedding []float32, limit int) ([]CodeEntity, error)
}

// CodeEntity represents a code entity for linking
type CodeEntity struct {
	ID         uuid.UUID `json:"id"`
	ProjectID  uuid.UUID `json:"project_id"`
	FilePath   string    `json:"file_path"`
	SymbolName string    `json:"symbol_name"`
	SymbolType string    `json:"symbol_type"`
	Language   string    `json:"language"`
	Embedding  []float32 `json:"embedding,omitempty"`
}

// TraceLink represents a traceability link between doc and code
type TraceLink struct {
	ID         uuid.UUID `json:"id"`
	ProjectID  uuid.UUID `json:"project_id"`
	SourceType string    `json:"source_type"` // "doc" or "code"
	SourceID   uuid.UUID `json:"source_id"`
	TargetType string    `json:"target_type"`
	TargetID   uuid.UUID `json:"target_id"`
	LinkType   string    `json:"link_type"` // documents, mentions, implements
	Confidence float64   `json:"confidence"`
	Evidence   string    `json:"evidence"`
	CreatedAt  time.Time `json:"created_at"`
}

// NewLinker creates a new document-to-code linker
func NewLinker(docRepo Repository, codeRepo CodeEntityRepository) *Linker {
	return &Linker{
		docRepo:  docRepo,
		codeRepo: codeRepo,
	}
}

// LinkDocToCode creates links between documentation entities and code entities
func (l *Linker) LinkDocToCode(ctx context.Context, projectID uuid.UUID, docEntityID uuid.UUID) ([]TraceLink, error) {
	// Get the doc entity
	docEntity, err := l.docRepo.GetDocEntity(ctx, docEntityID)
	if err != nil {
		return nil, err
	}

	links := make([]TraceLink, 0)
	links = l.appendCodeRefLinks(ctx, projectID, docEntityID, docEntity.CodeRefs, links)
	links = l.appendAPIRefLinks(ctx, projectID, docEntityID, docEntity.APIRefs, links)

	return links, nil
}

func (l *Linker) appendCodeRefLinks(
	ctx context.Context, projectID, docEntityID uuid.UUID, codeRefs []CodeRef, links []TraceLink,
) []TraceLink {
	for _, codeRef := range codeRefs {
		links = l.appendFilePathLinks(ctx, projectID, docEntityID, codeRef, links)
		links = l.appendSymbolLinks(ctx, projectID, docEntityID, codeRef, links)
	}
	return links
}

func (l *Linker) appendFilePathLinks(
	ctx context.Context, projectID, docEntityID uuid.UUID, codeRef CodeRef, links []TraceLink,
) []TraceLink {
	if codeRef.Type != "file" || codeRef.FilePath == "" {
		return links
	}
	codeEntities, err := l.codeRepo.FindByFilePath(ctx, projectID, codeRef.FilePath)
	if err != nil {
		return links
	}

	for _, ce := range codeEntities {
		links = append(links, newTraceLink(
			projectID, docEntityID, ce.ID, "documents", codeRef.Confidence,
			"File path reference: "+codeRef.FilePath,
		))
	}
	return links
}

func (l *Linker) appendSymbolLinks(
	ctx context.Context, projectID, docEntityID uuid.UUID, codeRef CodeRef, links []TraceLink,
) []TraceLink {
	if codeRef.Type != "function" && codeRef.Type != "class" {
		return links
	}
	codeEntities, err := l.codeRepo.FindBySymbolName(ctx, projectID, codeRef.Name)
	if err != nil {
		return links
	}

	for _, ce := range codeEntities {
		links = append(links, newTraceLink(
			projectID, docEntityID, ce.ID, "mentions",
			codeRef.Confidence*docLinkSymbolConfidenceScale, "Symbol reference: "+codeRef.Name,
		))
	}
	return links
}

func (l *Linker) appendAPIRefLinks(
	ctx context.Context, projectID, docEntityID uuid.UUID, apiRefs []APIRef, links []TraceLink,
) []TraceLink {
	for _, apiRef := range apiRefs {
		searchName := extractAPIName(apiRef.Path)
		codeEntities, err := l.codeRepo.FindBySymbolName(ctx, projectID, searchName)
		if err != nil {
			continue
		}

		for _, ce := range codeEntities {
			if ce.SymbolType == "handler" || ce.SymbolType == "route" || ce.SymbolType == "endpoint" {
				evidence := "API endpoint: " + apiRef.Method + " " + apiRef.Path
				links = append(links, newTraceLink(projectID, docEntityID, ce.ID, "documents", docLinkAPIConfidence, evidence))
			}
		}
	}
	return links
}

func newTraceLink(
	projectID, docEntityID, targetID uuid.UUID, linkType string, confidence float64, evidence string,
) TraceLink {
	return TraceLink{
		ID:         uuid.New(),
		ProjectID:  projectID,
		SourceType: "doc",
		SourceID:   docEntityID,
		TargetType: "code",
		TargetID:   targetID,
		LinkType:   linkType,
		Confidence: confidence,
		Evidence:   evidence,
		CreatedAt:  time.Now(),
	}
}

// extractAPIName extracts a searchable name from an API path
func extractAPIName(path string) string {
	// Remove version prefix
	path = strings.TrimPrefix(path, "/api/v1/")
	path = strings.TrimPrefix(path, "/api/v2/")
	path = strings.TrimPrefix(path, "/api/")
	path = strings.TrimPrefix(path, "/")

	// Get the resource name
	parts := strings.Split(path, "/")
	if len(parts) > 0 {
		// Remove path parameters
		name := parts[0]
		name = strings.TrimPrefix(name, "{")
		name = strings.TrimSuffix(name, "}")
		return name
	}

	return path
}
