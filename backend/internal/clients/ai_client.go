// Package clients provides clients functionality.
package clients

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"
)

const (
	streamChatEventBuffer = 10
	streamChatTimeout     = 10 * time.Minute
)

// AIClient provides HTTP client for Python AI service communication
type AIClient struct {
	pythonClient *PythonServiceClient
}

// StreamChatRequest represents a request for streaming chat with AI
type StreamChatRequest struct {
	Message   string                 `json:"message"`
	Context   map[string]interface{} `json:"context,omitempty"`
	ProjectID string                 `json:"project_id"`
	UserID    string                 `json:"user_id"`
}

// AnalyzeRequest represents a request for non-streaming AI analysis
type AnalyzeRequest struct {
	Text      string `json:"text"`
	ProjectID string `json:"project_id"`
}

// AnalysisResult represents the result of an AI analysis
type AnalysisResult struct {
	Analysis    string                 `json:"analysis"`
	Confidence  float64                `json:"confidence"`
	Suggestions []string               `json:"suggestions"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// SSEEvent represents a Server-Sent Event from AI streaming
type SSEEvent struct {
	Type    string                 `json:"type"` // "delta", "complete", "error", "metadata"
	Content string                 `json:"content,omitempty"`
	Delta   string                 `json:"delta,omitempty"`
	Data    map[string]interface{} `json:"data,omitempty"`
	Error   string                 `json:"error,omitempty"`
}

// NewAIClient creates a new AI service client
func NewAIClient(pythonClient *PythonServiceClient) *AIClient {
	return &AIClient{
		pythonClient: pythonClient,
	}
}

// StreamChat initiates a streaming chat with AI service
// Returns channels for SSE events and errors
func (aiClient *AIClient) StreamChat(
	ctx context.Context,
	req StreamChatRequest,
) (<-chan SSEEvent, <-chan error) {
	eventChan := make(chan SSEEvent, streamChatEventBuffer)
	errChan := make(chan error, 1)

	go func() {
		defer close(eventChan)
		defer close(errChan)

		if err := aiClient.streamChat(ctx, req, eventChan); err != nil {
			errChan <- err
		}
	}()

	return eventChan, errChan
}

func (aiClient *AIClient) streamChat(
	ctx context.Context,
	req StreamChatRequest,
	eventChan chan<- SSEEvent,
) error {
	httpReq, err := aiClient.buildStreamRequest(ctx, req)
	if err != nil {
		return err
	}

	resp, err := aiClient.doStreamRequest(httpReq)
	if err != nil {
		return err
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing AI stream response", "error", err)
		}
	}()

	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("request failed with status %d: %w", resp.StatusCode, err)
		}
		return fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	return aiClient.consumeSSE(ctx, resp.Body, eventChan)
}

func (aiClient *AIClient) buildStreamRequest(ctx context.Context, req StreamChatRequest) (*http.Request, error) {
	url := aiClient.pythonClient.baseURL + "/api/v1/ai/stream-chat"
	jsonData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "text/event-stream")
	httpReq.Header.Set("Cache-Control", "no-cache")
	httpReq.Header.Set("Connection", "keep-alive")
	if aiClient.pythonClient.serviceToken != "" {
		httpReq.Header.Set("Authorization", "Bearer "+aiClient.pythonClient.serviceToken)
	}

	return httpReq, nil
}

func (aiClient *AIClient) doStreamRequest(req *http.Request) (*http.Response, error) {
	client := &http.Client{Timeout: streamChatTimeout}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	return resp, nil
}

func (aiClient *AIClient) consumeSSE(ctx context.Context, body io.Reader, eventChan chan<- SSEEvent) error {
	reader := bufio.NewReader(body)
	for {
		done, err := aiClient.processSSEStream(ctx, reader, eventChan)
		if err != nil {
			return err
		}
		if done {
			return nil
		}
	}
}

func (aiClient *AIClient) processSSEStream(
	ctx context.Context,
	reader *bufio.Reader,
	eventChan chan<- SSEEvent,
) (bool, error) {
	if err := checkSSEContext(ctx); err != nil {
		return false, err
	}

	payload, err := readSSEPayload(reader)
	if err != nil {
		if errors.Is(err, io.EOF) {
			return true, nil
		}
		return false, err
	}
	if payload == nil {
		return false, nil
	}

	event, ok := parseSSEEvent(payload)
	if !ok {
		return false, nil
	}

	if err := sendSSEEvent(ctx, eventChan, event); err != nil {
		return false, err
	}

	done, err := handleSSETerminal(event)
	if err != nil {
		return false, err
	}
	return done, nil
}

func checkSSEContext(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		return nil
	}
}

func readSSEPayload(reader *bufio.Reader) ([]byte, error) {
	line, err := reader.ReadBytes('\n')
	if err != nil {
		if errors.Is(err, io.EOF) {
			return nil, io.EOF
		}
		return nil, fmt.Errorf("failed to read stream: %w", err)
	}

	if !isSSEDataLine(line) {
		return nil, nil
	}

	return line[6:], nil
}

func sendSSEEvent(ctx context.Context, eventChan chan<- SSEEvent, event SSEEvent) error {
	select {
	case eventChan <- event:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func handleSSETerminal(event SSEEvent) (bool, error) {
	if event.Type == "complete" {
		return true, nil
	}
	if event.Type == "error" {
		return true, fmt.Errorf("stream error: %s", event.Error)
	}
	return false, nil
}

func isSSEDataLine(line []byte) bool {
	return len(line) > 6 && string(line[:6]) == "data: "
}

func parseSSEEvent(payload []byte) (SSEEvent, bool) {
	var event SSEEvent
	if err := json.Unmarshal(payload, &event); err != nil {
		return SSEEvent{}, false
	}
	return event, true
}

// Analyze performs non-streaming AI analysis
func (aiClient *AIClient) Analyze(ctx context.Context, text string, projectID string) (*AnalysisResult, error) {
	req := AnalyzeRequest{
		Text:      text,
		ProjectID: projectID,
	}

	var result AnalysisResult
	err := aiClient.pythonClient.DelegateRequest(
		ctx,
		"POST",
		"/api/v1/ai/analyze",
		req,
		&result,
		false, // No caching for AI analysis (always fresh)
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("AI analysis failed: %w", err)
	}

	return &result, nil
}
