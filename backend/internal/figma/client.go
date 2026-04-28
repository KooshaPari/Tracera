// Package figma provides Figma API clients and sync helpers.
package figma

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"net/url"
	"strings"
	"time"
)

const defaultFigmaTimeout = 30 * time.Second

// Client represents the Figma API client
type Client struct {
	token      string
	baseURL    string
	httpClient *http.Client
	config     ClientConfig
}

// NewClient creates a new Figma API client
func NewClient(config ClientConfig) (*Client, error) {
	if config.Token == "" {
		return nil, errors.New("figma token is required")
	}

	if config.BaseURL == "" {
		config.BaseURL = "https://api.figma.com/v1"
	}

	if config.Timeout == 0 {
		config.Timeout = defaultFigmaTimeout
	}

	return &Client{
		token:   config.Token,
		baseURL: config.BaseURL,
		config:  config,
		httpClient: &http.Client{
			Timeout: config.Timeout,
		},
	}, nil
}

// HealthCheck verifies the Figma API token is valid
func (client *Client) HealthCheck(ctx context.Context) error {
	if client.token == "" {
		return errors.New("figma token not configured")
	}

	// Make a simple request to verify token
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, client.baseURL+"/me", nil)
	if err != nil {
		return fmt.Errorf("failed to create health check request: %w", err)
	}

	client.setAuthHeader(req)
	resp, err := client.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("health check request failed: %w", err)
	}
	defer closeResponseBody(resp)

	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return fmt.Errorf("health check failed to read response body: %w", readErr)
		}
		return fmt.Errorf("health check failed with status %d: %s", resp.StatusCode, body)
	}

	return nil
}

// GetFileMetadata retrieves metadata for a Figma file
func (client *Client) GetFileMetadata(ctx context.Context, fileKey string) (*FileMetadata, error) {
	if fileKey == "" {
		return nil, errors.New("file key is required")
	}

	endpoint := fmt.Sprintf("%s/files/%s/versions", client.baseURL, url.PathEscape(fileKey))
	resp, err := client.makeRequest(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get file metadata: %w", err)
	}

	defer closeResponseBody(resp)
	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return nil, fmt.Errorf("failed to read file metadata response: %w", readErr)
		}
		return nil, fmt.Errorf("failed to get file metadata: status %d: %s", resp.StatusCode, body)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode file metadata response: %w", err)
	}

	// Extract relevant metadata
	metadata := &FileMetadata{
		Key:          fileKey,
		Name:         extractString(result, "name"),
		ThumbnailURL: extractString(result, "thumbnailUrl"),
		EditorType:   extractString(result, "editorType"),
	}

	// Parse lastModified if available
	if lastModStr, ok := result["lastModified"].(string); ok {
		if t, err := time.Parse(time.RFC3339, lastModStr); err == nil {
			metadata.LastModified = t
		}
	}

	return metadata, nil
}

// GetFile retrieves complete file data including nodes
func (client *Client) GetFile(ctx context.Context, fileKey string, opts ...QueryOption) (*FileResponse, error) {
	if fileKey == "" {
		return nil, errors.New("file key is required")
	}

	queryParams := buildQueryParams(opts)
	endpoint := buildFileEndpoint(client.baseURL, fileKey, queryParams)

	resp, err := client.makeRequest(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get file: %w", err)
	}

	defer closeResponseBody(resp)
	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return nil, fmt.Errorf("failed to read file response: %w", readErr)
		}
		return nil, fmt.Errorf("failed to get file: status %d: %s", resp.StatusCode, body)
	}

	return parseFileResponse(resp.Body)
}

// GetNodes retrieves specific nodes from a file
func (client *Client) GetNodes(ctx context.Context, fileKey string, nodeIDs []string) (map[string]*Node, error) {
	if fileKey == "" {
		return nil, errors.New("file key is required")
	}
	if len(nodeIDs) == 0 {
		return nil, errors.New("at least one node ID is required")
	}

	queryParams := buildNodesQueryParams(nodeIDs)
	endpoint := buildNodesEndpoint(client.baseURL, fileKey, queryParams)

	resp, err := client.makeRequest(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get nodes: %w", err)
	}

	defer closeResponseBody(resp)
	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return nil, fmt.Errorf("failed to read nodes response: %w", readErr)
		}
		return nil, fmt.Errorf("failed to get nodes: status %d: %s", resp.StatusCode, body)
	}

	return parseNodesResponse(resp.Body)
}

// ExportImages retrieves image exports for specified nodes
func (client *Client) ExportImages(
	ctx context.Context,
	fileKey string,
	nodeIDs []string,
	settings ExportSettings,
) (map[string]string, error) {
	if fileKey == "" {
		return nil, errors.New("file key is required")
	}
	if len(nodeIDs) == 0 {
		return nil, errors.New("at least one node ID is required")
	}

	queryParams := buildExportImagesQuery(nodeIDs, settings)

	endpoint := fmt.Sprintf("%s/images/%s", client.baseURL, url.PathEscape(fileKey))
	if len(queryParams) > 0 {
		endpoint = endpoint + "?" + queryParams.Encode()
	}

	resp, err := client.makeRequest(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to export images: %w", err)
	}

	defer closeResponseBody(resp)
	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return nil, fmt.Errorf("failed to read export response: %w", readErr)
		}
		return nil, fmt.Errorf("failed to export images: status %d: %s", resp.StatusCode, body)
	}

	var result ImageExportResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode image export response: %w", err)
	}

	if result.Err != "" {
		return nil, fmt.Errorf("image export error: %s", result.Err)
	}

	return result.Images, nil
}

func buildExportImagesQuery(nodeIDs []string, settings ExportSettings) url.Values {
	queryParams := url.Values{}
	queryParams.Set("ids", strings.Join(nodeIDs, ","))
	queryParams.Set("format", string(settings.Format))

	if settings.Scale > 0 {
		queryParams.Set("scale", fmt.Sprintf("%.1f", settings.Scale))
	}
	if settings.SVGIncludeID {
		queryParams.Set("svg_include_id", "true")
	}
	if settings.SVGSimplifyStroke {
		queryParams.Set("svg_simplify_stroke", "true")
	}
	if settings.SVGUseAbsoluteBounds {
		queryParams.Set("svg_use_absolute_bounds", "true")
	}
	if settings.PDFIncludeID {
		queryParams.Set("pdf_include_id", "true")
	}

	return queryParams
}

func buildQueryParams(opts []QueryOption) url.Values {
	queryParams := url.Values{}
	for _, opt := range opts {
		opt(&queryParams)
	}
	return queryParams
}

func buildFileEndpoint(baseURL, fileKey string, queryParams url.Values) string {
	endpoint := fmt.Sprintf("%s/files/%s", baseURL, url.PathEscape(fileKey))
	if len(queryParams) > 0 {
		endpoint = endpoint + "?" + queryParams.Encode()
	}
	return endpoint
}

func parseFileResponse(body io.Reader) (*FileResponse, error) {
	var result map[string]interface{}
	if err := json.NewDecoder(body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode file response: %w", err)
	}

	fileData := &FileResponse{
		Name:    extractString(result, "name"),
		Role:    extractString(result, "role"),
		Version: extractString(result, "version"),
		Pages:   extractPageNodes(result),
		Nodes:   nil,
		Schemas: nil,
	}

	if nodes, ok := result["nodes"].(map[string]interface{}); ok {
		fileData.Nodes = nodes
	}

	return fileData, nil
}

func extractPageNodes(result map[string]interface{}) []PageNode {
	pages := make([]PageNode, 0)
	rawPages, ok := result["pages"].([]interface{})
	if !ok {
		return pages
	}

	for _, page := range rawPages {
		pageMap, ok := page.(map[string]interface{})
		if !ok {
			continue
		}
		pages = append(pages, PageNode{
			ID:   extractString(pageMap, "id"),
			Name: extractString(pageMap, "name"),
		})
	}

	return pages
}

func buildNodesQueryParams(nodeIDs []string) url.Values {
	queryParams := url.Values{}
	queryParams.Set("ids", strings.Join(nodeIDs, ","))
	return queryParams
}

func buildNodesEndpoint(baseURL, fileKey string, queryParams url.Values) string {
	endpoint := fmt.Sprintf("%s/files/%s/nodes", baseURL, url.PathEscape(fileKey))
	if len(queryParams) > 0 {
		endpoint = endpoint + "?" + queryParams.Encode()
	}
	return endpoint
}

func parseNodesResponse(body io.Reader) (map[string]*Node, error) {
	var result map[string]interface{}
	if err := json.NewDecoder(body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode nodes response: %w", err)
	}
	return extractNodes(result), nil
}

func extractNodes(result map[string]interface{}) map[string]*Node {
	nodes := make(map[string]*Node)
	nodesMap, ok := result["nodes"].(map[string]interface{})
	if !ok {
		return nodes
	}

	for nodeID, nodeData := range nodesMap {
		nodeMap, ok := nodeData.(map[string]interface{})
		if !ok {
			continue
		}
		nodes[nodeID] = parseNode(nodeMap)
	}

	return nodes
}

// GetComponents retrieves all components in a file
func (client *Client) GetComponents(ctx context.Context, fileKey string) (map[string]interface{}, error) {
	return client.getComponentData(ctx, fileKey, "components", "components")
}

// GetComponentSets retrieves all component sets in a file
func (client *Client) GetComponentSets(ctx context.Context, fileKey string) (map[string]interface{}, error) {
	return client.getComponentData(ctx, fileKey, "component_sets", "component sets")
}

func (client *Client) getComponentData(
	ctx context.Context,
	fileKey string,
	resourcePath string,
	resourceLabel string,
) (map[string]interface{}, error) {
	if fileKey == "" {
		return nil, errors.New("file key is required")
	}

	endpoint := fmt.Sprintf("%s/files/%s/%s", client.baseURL, url.PathEscape(fileKey), resourcePath)

	resp, err := client.makeRequest(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get %s: %w", resourceLabel, err)
	}

	defer closeResponseBody(resp)
	if resp.StatusCode != http.StatusOK {
		body, readErr := readResponseBody(resp)
		if readErr != nil {
			return nil, fmt.Errorf("failed to read %s response: %w", resourceLabel, readErr)
		}
		return nil, fmt.Errorf("failed to get %s: status %d: %s", resourceLabel, resp.StatusCode, body)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode %s response: %w", resourceLabel, err)
	}

	return result, nil
}

// makeRequest is a helper method to make authenticated HTTP requests
func (client *Client) makeRequest(
	ctx context.Context,
	method string,
	endpoint string,
	body io.Reader,
) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, method, endpoint, body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	client.setAuthHeader(req)
	req.Header.Set("Content-Type", "application/json")

	return client.httpClient.Do(req)
}

func closeResponseBody(resp *http.Response) {
	if resp == nil || resp.Body == nil {
		return
	}
	if err := resp.Body.Close(); err != nil {
		slog.Error("failed to close figma response body", "error", err)
	}
}

func readResponseBody(resp *http.Response) (string, error) {
	if resp == nil || resp.Body == nil {
		return "", errors.New("response body is nil")
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response body: %w", err)
	}
	return string(body), nil
}

// setAuthHeader adds the authorization header to the request
func (client *Client) setAuthHeader(req *http.Request) {
	req.Header.Set("X-Figma-Token", client.token)
}

// Close closes the HTTP client
func (client *Client) Close() error {
	if client.httpClient != nil {
		client.httpClient.CloseIdleConnections()
	}
	return nil
}

// QueryOption is a function type for setting query parameters
type QueryOption func(*url.Values)

// WithGeometry includes geometry data in the response
func WithGeometry() QueryOption {
	return func(q *url.Values) {
		q.Set("geometry", "true")
	}
}

// WithPluginData includes plugin data in the response
func WithPluginData(pluginID string) QueryOption {
	return func(q *url.Values) {
		q.Set("plugin_data", pluginID)
	}
}

// WithBranchData includes branch data in the response
func WithBranchData(branchID string) QueryOption {
	return func(q *url.Values) {
		q.Set("branch_data", "true")
		q.Set("version", branchID)
	}
}

// Helper functions for parsing responses
func extractString(m map[string]interface{}, key string) string {
	if v, ok := m[key].(string); ok {
		return v
	}
	return ""
}

func parseNode(data map[string]interface{}) *Node {
	node := &Node{
		ID:             extractString(data, "id"),
		Name:           extractString(data, "name"),
		Type:           extractString(data, "type"),
		ParentID:       extractString(data, "parentId"),
		ComponentSetID: extractString(data, "componentSetId"),
		Description:    extractString(data, "description"),
	}

	if v, ok := data["isMainComponent"].(bool); ok {
		node.IsMainComponent = v
	}
	if v, ok := data["isComponent"].(bool); ok {
		node.IsComponent = v
	}
	if v, ok := data["isAsset"].(bool); ok {
		node.IsAsset = v
	}

	if modStr, ok := data["modifiedAt"].(string); ok {
		if t, err := time.Parse(time.RFC3339, modStr); err == nil {
			node.ModifiedAt = t
		}
	}

	if properties, ok := data["properties"].(map[string]interface{}); ok {
		node.Properties = properties
	}

	return node
}
