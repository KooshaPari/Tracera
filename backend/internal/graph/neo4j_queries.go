package graph

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func recordString(values []any, idx int) string {
	if idx >= len(values) {
		return ""
	}
	s, ok := values[idx].(string)
	if !ok {
		return ""
	}
	return s
}

// Model represents a model node in Neo4j
type Model struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Version string `json:"version"`
	Type    string `json:"type"`
}

// GetModels retrieves all models for a project
func (c *Neo4jClient) GetModels(ctx context.Context, projectCtx *ProjectContext) ([]Model, error) {
	query := `
	MATCH (m:Model {project_id: $projectId})
	RETURN m.id as id, m.name as name, m.version as version, m.type as type
	`

	result, err := c.ExecuteQuery(ctx, projectCtx, query, nil)
	if err != nil {
		return nil, err
	}

	var models []Model
	for result.Next(ctx) {
		record := result.Record()
		models = append(models, Model{
			ID:      recordString(record.Values, 0),
			Name:    recordString(record.Values, 1),
			Version: recordString(record.Values, 2),
			Type:    recordString(record.Values, 3),
		})
	}

	return models, result.Err()
}

// CreateModel creates a new model node
func (c *Neo4jClient) CreateModel(ctx context.Context, projectCtx *ProjectContext, model Model) error {
	query := `
	MATCH (p:Project {id: $projectId})
	CREATE (m:Model {
		id: $modelId,
		project_id: $projectId,
		namespace: $namespace,
		name: $name,
		version: $version,
		type: $type,
		created_at: timestamp()
	})
	CREATE (p)-[:OWNS]->(m)
	RETURN m
	`

	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	_, err := session.Run(ctx, query, map[string]interface{}{
		"projectId": projectCtx.ProjectID,
		"namespace": string(projectCtx.Namespace),
		"modelId":   model.ID,
		"name":      model.Name,
		"version":   model.Version,
		"type":      model.Type,
	})

	return err
}

// CreateRelationship creates a relationship between two nodes
func (c *Neo4jClient) CreateRelationship(ctx context.Context, projectCtx *ProjectContext, sourceID, targetID, relationType string) error {
	query := fmt.Sprintf(`
	MATCH (source {id: $sourceId, project_id: $projectId})
	MATCH (target {id: $targetId, project_id: $projectId})
	CREATE (source)-[:%s {created_at: timestamp()}]->(target)
	`, relationType)

	session := c.driver.NewSession(ctx, neo4j.SessionConfig{})
	defer closeNeo4jSession(ctx, session)

	_, err := session.Run(ctx, query, map[string]interface{}{
		"projectId": projectCtx.ProjectID,
		"sourceId":  sourceID,
		"targetId":  targetID,
	})

	return err
}

// GetRelatedNodes retrieves nodes related to a given node
func (c *Neo4jClient) GetRelatedNodes(ctx context.Context, projectCtx *ProjectContext, nodeID string, direction string) ([]Model, error) {
	var query string

	switch direction {
	case "outgoing":
		query = `
		MATCH (n {id: $nodeId, project_id: $projectId})-[]->(related)
		RETURN related.id as id, related.name as name, related.version as version, related.type as type
		`
	case "incoming":
		query = `
		MATCH (related)-[]->(n {id: $nodeId, project_id: $projectId})
		RETURN related.id as id, related.name as name, related.version as version, related.type as type
		`
	default:
		query = `
		MATCH (n {id: $nodeId, project_id: $projectId})-[]-(related)
		RETURN related.id as id, related.name as name, related.version as version, related.type as type
		`
	}

	result, err := c.ExecuteQuery(ctx, projectCtx, query, map[string]interface{}{
		"nodeId": nodeID,
	})
	if err != nil {
		return nil, err
	}

	var models []Model
	for result.Next(ctx) {
		record := result.Record()
		models = append(models, Model{
			ID:      recordString(record.Values, 0),
			Name:    recordString(record.Values, 1),
			Version: recordString(record.Values, 2),
			Type:    recordString(record.Values, 3),
		})
	}

	return models, result.Err()
}
