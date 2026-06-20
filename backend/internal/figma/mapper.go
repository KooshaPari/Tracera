package figma

import (
	"fmt"
	"strings"
	"time"
)

const variantNameKVParts = 2

// Mapper handles conversion of Figma nodes to LibraryComponent records
type Mapper struct {
	fileKey   string
	projectID string
	baseURL   string
}

// NewMapper creates a new Figma node mapper
func NewMapper(projectID, fileKey string) *Mapper {
	return &Mapper{
		fileKey:   fileKey,
		projectID: projectID,
		baseURL:   "https://www.figma.com",
	}
}

// MapNodeToComponent converts a Figma node to a LibraryComponent
func (mapper *Mapper) MapNodeToComponent(node *Node) *LibraryComponent {
	if node == nil {
		return nil
	}

	component := &LibraryComponent{
		ID:          node.ID,
		ProjectID:   mapper.projectID,
		FigmaNodeID: node.ID,
		Name:        node.Name,
		Description: node.Description,
		Properties:  node.Properties,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// Extract category from component name (e.g., "Button/Primary" -> "Button")
	component.Category = extractCategory(node.Name)

	// Generate thumbnail URL if it's a component
	if node.IsComponent || node.IsMainComponent {
		component.ThumbnailURL = mapper.generateThumbnailURL(node.ID)
	}

	// Extract variants if this is a component set
	if node.ComponentSetID != "" || node.IsMainComponent {
		component.Variants = mapper.extractVariants(node)
	}

	return component
}

// MapNodesToComponents converts multiple Figma nodes to LibraryComponents
func (mapper *Mapper) MapNodesToComponents(nodes map[string]*Node) []*LibraryComponent {
	components := make([]*LibraryComponent, 0)

	for _, node := range nodes {
		// Only map actual components
		if node.IsComponent || node.IsMainComponent {
			component := mapper.MapNodeToComponent(node)
			if component != nil {
				components = append(components, component)
			}
		}
	}

	return components
}

// extractVariants extracts variant information from a component node
func (mapper *Mapper) extractVariants(node *Node) []ComponentVariant {
	variants := make([]ComponentVariant, 0)

	if len(node.VariantGroupProperties) == 0 {
		// If no variant properties defined, this is a single variant
		if node.IsMainComponent || node.IsComponent {
			variants = append(variants, ComponentVariant{
				ID:         node.ID,
				Name:       node.Name,
				Properties: make(map[string]string),
			})
		}
		return variants
	}

	// Parse variant group properties to determine variants
	// This would typically be processed in conjunction with the actual variant nodes
	// For now, we structure the variant metadata
	for propName, variantProp := range node.VariantGroupProperties {
		for _, option := range variantProp.Options {
			variant := ComponentVariant{
				Name: fmt.Sprintf("%s=%s", propName, option),
				Properties: map[string]string{
					propName: option,
				},
				Description: node.Description,
			}
			variants = append(variants, variant)
		}
	}

	return variants
}

// MapNodeToSyncState converts a Figma node to a SyncState record.
func (mapper *Mapper) MapNodeToSyncState(node *Node, itemID *string, componentID *string) *SyncState {
	if node == nil {
		return nil
	}

	now := time.Now()
	figmaURL := mapper.generateFigmaURL(node.ID)

	syncState := &SyncState{
		ProjectID:       mapper.projectID,
		ItemID:          itemID,
		ComponentID:     componentID,
		FileKey:         mapper.fileKey,
		NodeID:          node.ID,
		NodeName:        &node.Name,
		FigmaURL:        &figmaURL,
		NodeType:        &node.Type,
		SyncStatus:      SyncStatusUnlinked,
		FigmaModifiedAt: &now,
		CreatedAt:       now,
		UpdatedAt:       now,
		HasConflict:     false,
		Metadata:        make(map[string]interface{}),
		SyncMetadata:    make(map[string]interface{}),
	}

	// Set modified time from node if available
	if !node.ModifiedAt.IsZero() {
		syncState.FigmaModifiedAt = &node.ModifiedAt
	}

	// Add component-specific metadata
	if node.IsComponent || node.IsMainComponent {
		syncState.Metadata["is_component"] = true
		syncState.Metadata["is_main_component"] = node.IsMainComponent
	}

	if node.ComponentSetID != "" {
		syncState.Metadata["component_set_id"] = node.ComponentSetID
	}

	if len(node.VariantGroupProperties) > 0 {
		syncState.Metadata["variant_properties"] = node.VariantGroupProperties
	}

	return syncState
}

// ExtractComponentProperties extracts relevant component properties from a Figma node
func (mapper *Mapper) ExtractComponentProperties(node *Node) map[string]interface{} {
	properties := make(map[string]interface{})

	if node == nil {
		return properties
	}

	mapper.addBasicComponentProperties(properties, node)
	mapper.addVariantProperties(properties, node)
	mapper.addDocumentationLinks(properties, node)
	mergeAdditionalProperties(properties, node.Properties)

	return properties
}

func (mapper *Mapper) addBasicComponentProperties(properties map[string]interface{}, node *Node) {
	properties["name"] = node.Name
	properties["type"] = node.Type
	properties["description"] = node.Description
	properties["is_component"] = node.IsComponent
	properties["is_main_component"] = node.IsMainComponent
}

func (mapper *Mapper) addVariantProperties(properties map[string]interface{}, node *Node) {
	if len(node.VariantGroupProperties) == 0 {
		return
	}

	variantInfo := make(map[string]interface{})
	for propName, propDef := range node.VariantGroupProperties {
		variantInfo[propName] = map[string]interface{}{
			"type":    propDef.Type,
			"default": propDef.Default,
			"options": propDef.Options,
		}
	}
	properties["variants"] = variantInfo
}

func (mapper *Mapper) addDocumentationLinks(properties map[string]interface{}, node *Node) {
	if len(node.DocumentationLinks) == 0 {
		return
	}

	docLinks := make([]string, 0)
	for _, link := range node.DocumentationLinks {
		docLinks = append(docLinks, link.URI)
	}
	properties["documentation_links"] = docLinks
}

func mergeAdditionalProperties(properties map[string]interface{}, extra map[string]interface{}) {
	if extra == nil {
		return
	}

	for key, value := range extra {
		if _, exists := properties[key]; !exists {
			properties[key] = value
		}
	}
}

// ParseVariantName parses a Figma component variant name into properties
// Example: "Button=Primary, Size=Large" -> {"Button": "Primary", "Size": "Large"}
func ParseVariantName(variantName string) map[string]string {
	properties := make(map[string]string)

	// Split by comma to get individual properties
	parts := strings.Split(variantName, ",")
	for _, part := range parts {
		part = strings.TrimSpace(part)
		// Split by equals to get key and value
		kv := strings.Split(part, "=")
		if len(kv) == variantNameKVParts {
			key := strings.TrimSpace(kv[0])
			value := strings.TrimSpace(kv[1])
			properties[key] = value
		}
	}

	return properties
}

// VariantNameFromProperties constructs a variant name from properties
// Example: {"Button": "Primary", "Size": "Large"} -> "Button=Primary, Size=Large"
func VariantNameFromProperties(props map[string]string) string {
	parts := make([]string, 0, len(props))
	for key, value := range props {
		parts = append(parts, fmt.Sprintf("%s=%s", key, value))
	}
	return strings.Join(parts, ", ")
}

// generateFigmaURL creates a Figma URL for a specific node
func (mapper *Mapper) generateFigmaURL(nodeID string) string {
	return fmt.Sprintf("%s/file/%s?node-id=%s", mapper.baseURL, mapper.fileKey, nodeID)
}

// generateThumbnailURL creates a thumbnail URL for image export
func (mapper *Mapper) generateThumbnailURL(nodeID string) string {
	// This would typically be populated from actual image exports
	// For now, return a placeholder that can be resolved later
	return fmt.Sprintf("figma://thumbnail/%s/%s", mapper.fileKey, nodeID)
}

// extractCategory extracts a category from a component name
// Example: "Button/Primary" -> "Button"
func extractCategory(name string) string {
	parts := strings.Split(name, "/")
	if len(parts) > 0 {
		return parts[0]
	}
	return name
}

// ExtractComponentPath extracts the full path from a component name
// Example: "Button/Primary/Small" -> ["Button", "Primary", "Small"]
func ExtractComponentPath(name string) []string {
	parts := strings.Split(name, "/")
	result := make([]string, 0)
	for _, part := range parts {
		if trimmed := strings.TrimSpace(part); trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

// BuildComponentPath constructs a component path from parts
// Example: ["Button", "Primary"] -> "Button/Primary"
func BuildComponentPath(parts []string) string {
	return strings.Join(parts, "/")
}

// NormalizeComponentName normalizes a component name for consistent comparison
func NormalizeComponentName(name string) string {
	return strings.TrimSpace(strings.ToLower(name))
}

// CompareNodeVersions compares two node versions to detect changes
func CompareNodeVersions(old *Node, newNode *Node) SyncComparison {
	comparison := SyncComparison{
		NodeID:        newNode.ID,
		FigmaModified: newNode.ModifiedAt,
		IsSynced:      true,
	}

	if old == nil {
		comparison.IsSynced = false
		return comparison
	}

	// Compare names
	if old.Name != newNode.Name {
		comparison.IsSynced = false
		comparison.ConflictDetails += "Component name changed; "
	}

	// Compare descriptions
	if old.Description != newNode.Description {
		comparison.IsSynced = false
		comparison.ConflictDetails += "Description changed; "
	}

	// Compare component status
	if old.IsComponent != newNode.IsComponent || old.IsMainComponent != newNode.IsMainComponent {
		comparison.IsSynced = false
		comparison.ConflictDetails += "Component status changed; "
	}

	// Compare variant properties
	if len(old.VariantGroupProperties) != len(newNode.VariantGroupProperties) {
		comparison.IsSynced = false
		comparison.ConflictDetails += "Variant structure changed; "
	}

	return comparison
}
