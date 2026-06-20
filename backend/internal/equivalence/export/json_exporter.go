package export

import (
	"encoding/json"
	"errors"
	"io"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

// JSONExporter exports equivalence data to JSON format
type JSONExporter struct {
	includeEmbeddings bool
	includeMetadata   bool
	prettyPrint       bool
}

// NewJSONExporter creates a new JSON exporter
func NewJSONExporter(opts ...JSONExporterOption) *JSONExporter {
	exporter := &JSONExporter{
		includeEmbeddings: false,
		includeMetadata:   true,
		prettyPrint:       true,
	}
	for _, opt := range opts {
		opt(exporter)
	}
	return exporter
}

// JSONExporterOption is a functional option for JSONExporter
type JSONExporterOption func(*JSONExporter)

// WithEmbeddings includes embeddings in the export
func WithEmbeddings(include bool) JSONExporterOption {
	return func(exporter *JSONExporter) {
		exporter.includeEmbeddings = include
	}
}

// WithMetadata includes metadata in the export
func WithMetadata(include bool) JSONExporterOption {
	return func(exporter *JSONExporter) {
		exporter.includeMetadata = include
	}
}

// WithPrettyPrint enables/disables pretty printing
func WithPrettyPrint(pretty bool) JSONExporterOption {
	return func(exporter *JSONExporter) {
		exporter.prettyPrint = pretty
	}
}

// Export writes the equivalence data to JSON format
func (exporter *JSONExporter) Export(
	writer io.Writer,
	concepts []equivalence.CanonicalConcept,
	projections []equivalence.CanonicalProjection,
	links []equivalence.Link,
	projectID uuid.UUID,
	projectName string,
) error {
	if len(concepts) == 0 && len(projections) == 0 && len(links) == 0 {
		return errors.New("no data to export")
	}

	// Convert domain models to export format
	exportConcepts := convertConcepts(concepts, exporter.includeEmbeddings)
	exportProjections := convertProjections(projections, exporter.includeMetadata)
	exportLinks := convertLinks(links, exporter.includeMetadata)

	// Calculate statistics
	stats := calculateStatistics(concepts, projections, links)

	// Build export data
	exportData := &Data{
		Version:     FormatVersion,
		ExportedAt:  time.Now().UTC(),
		ProjectID:   projectID,
		ProjectName: projectName,
		Metadata: Metadata{
			IncludeEmbeddings: exporter.includeEmbeddings,
			IncludeMetadata:   exporter.includeMetadata,
		},
		CanonicalConcepts: exportConcepts,
		Projections:       exportProjections,
		EquivalenceLinks:  exportLinks,
		Statistics:        stats,
	}

	// Encode to JSON
	encoder := json.NewEncoder(writer)
	if exporter.prettyPrint {
		encoder.SetIndent("", "  ")
	}
	encoder.SetEscapeHTML(false)

	return encoder.Encode(exportData)
}
