package export

import (
	"errors"
	"io"
	"log/slog"
	"time"

	"github.com/google/uuid"
	"gopkg.in/yaml.v3"

	"github.com/kooshapari/tracertm-backend/internal/equivalence"
)

const yamlIndentSpaces = 2

// YAMLExporter exports equivalence data to YAML format
type YAMLExporter struct {
	includeEmbeddings bool
	includeMetadata   bool
}

// NewYAMLExporter creates a new YAML exporter
func NewYAMLExporter(opts ...YAMLExporterOption) *YAMLExporter {
	exporter := &YAMLExporter{
		includeEmbeddings: false,
		includeMetadata:   true,
	}
	for _, opt := range opts {
		opt(exporter)
	}
	return exporter
}

// YAMLExporterOption is a functional option for YAMLExporter
type YAMLExporterOption func(*YAMLExporter)

// WithYAMLEmbeddings includes embeddings in the export
func WithYAMLEmbeddings(include bool) YAMLExporterOption {
	return func(exporter *YAMLExporter) {
		exporter.includeEmbeddings = include
	}
}

// WithYAMLMetadata includes metadata in the export
func WithYAMLMetadata(include bool) YAMLExporterOption {
	return func(exporter *YAMLExporter) {
		exporter.includeMetadata = include
	}
}

// Export writes the equivalence data to YAML format
func (exporter *YAMLExporter) Export(
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

	// Encode to YAML
	encoder := yaml.NewEncoder(writer)
	encoder.SetIndent(yamlIndentSpaces)
	defer func() {
		if err := encoder.Close(); err != nil {
			slog.Error("failed to close YAML encoder", "error", err)
		}
	}()

	return encoder.Encode(exportData)
}
