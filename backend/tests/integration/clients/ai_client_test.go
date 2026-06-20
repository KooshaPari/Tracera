package clients_test

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
)

func TestAIClient_StreamChat(t *testing.T) {
	// Create mock SSE server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/api/v1/ai/stream-chat", r.URL.Path)
		assert.Equal(t, "text/event-stream", r.Header.Get("Accept"))

		// Send SSE events
		w.Header().Set("Content-Type", "text/event-stream")
		w.WriteHeader(http.StatusOK)

		// Send multiple events
		events := []string{
			`data: {"type":"delta","delta":"Hello"}` + "\n\n",
			`data: {"type":"delta","delta":" World"}` + "\n\n",
			`data: {"type":"complete","content":"Hello World"}` + "\n\n",
		}

		flusher, ok := w.(http.Flusher)
		require.True(t, ok)

		for _, event := range events {
			_, err := w.Write([]byte(event))
			require.NoError(t, err)
			flusher.Flush()
			time.Sleep(10 * time.Millisecond)
		}
	}))
	defer server.Close()

	// Create AI client
	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	aiClient := clients.NewAIClient(pythonClient)

	// Test streaming
	ctx := context.Background()
	req := clients.StreamChatRequest{
		Message:   "Test message",
		ProjectID: "test-project",
		UserID:    "test-user",
	}

	eventChan, errChan := aiClient.StreamChat(ctx, req)

	// Collect events
	var events []clients.SSEEvent
	var receivedError error

	done := make(chan bool)
	go func() {
		for {
			select {
			case event, ok := <-eventChan:
				if !ok {
					done <- true
					return
				}
				events = append(events, event)
			case err := <-errChan:
				receivedError = err
				done <- true
				return
			}
		}
	}()

	// Wait for completion
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("Timeout waiting for stream completion")
	}

	// Verify results
	assert.NoError(t, receivedError)
	assert.Len(t, events, 3)
	assert.Equal(t, "delta", events[0].Type)
	assert.Equal(t, "Hello", events[0].Delta)
	assert.Equal(t, "delta", events[1].Type)
	assert.Equal(t, " World", events[1].Delta)
	assert.Equal(t, "complete", events[2].Type)
	assert.Equal(t, "Hello World", events[2].Content)
}

func TestAIClient_StreamChat_ContextCancellation(t *testing.T) {
	// Create mock server with slow streaming
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.WriteHeader(http.StatusOK)

		flusher, _ := w.(http.Flusher)

		// Send one event then wait
		w.Write([]byte(`data: {"type":"delta","delta":"Start"}` + "\n\n"))
		flusher.Flush()

		// Wait indefinitely (will be cancelled)
		time.Sleep(10 * time.Second)
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	aiClient := clients.NewAIClient(pythonClient)

	// Test with cancellable context
	ctx, cancel := context.WithCancel(context.Background())
	req := clients.StreamChatRequest{
		Message:   "Test message",
		ProjectID: "test-project",
		UserID:    "test-user",
	}

	eventChan, errChan := aiClient.StreamChat(ctx, req)

	// Receive first event
	event := <-eventChan
	assert.Equal(t, "delta", event.Type)

	// Cancel context
	cancel()

	// Verify cancellation is handled
	select {
	case err := <-errChan:
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "context canceled")
	case <-time.After(2 * time.Second):
		t.Fatal("Expected error from context cancellation")
	}
}

func TestAIClient_StreamChat_ErrorEvent(t *testing.T) {
	// Create mock server that sends error
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.WriteHeader(http.StatusOK)

		flusher, _ := w.(http.Flusher)

		// Send error event
		w.Write([]byte(`data: {"type":"error","error":"Test error message"}` + "\n\n"))
		flusher.Flush()
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	aiClient := clients.NewAIClient(pythonClient)

	ctx := context.Background()
	req := clients.StreamChatRequest{
		Message:   "Test message",
		ProjectID: "test-project",
		UserID:    "test-user",
	}

	eventChan, errChan := aiClient.StreamChat(ctx, req)

	// Should receive error
	select {
	case err := <-errChan:
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "Test error message")
	case <-eventChan:
		// Also acceptable to receive error event first
	case <-time.After(2 * time.Second):
		t.Fatal("Expected error event")
	}
}

func TestAIClient_Analyze(t *testing.T) {
	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/api/v1/ai/analyze", r.URL.Path)

		// Return analysis result
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"analysis": "This is a test analysis",
			"confidence": 0.95,
			"suggestions": ["suggestion1", "suggestion2"],
			"metadata": {"key": "value"}
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	aiClient := clients.NewAIClient(pythonClient)

	ctx := context.Background()
	result, err := aiClient.Analyze(ctx, "Test text", "test-project")

	require.NoError(t, err)
	assert.Equal(t, "This is a test analysis", result.Analysis)
	assert.Equal(t, 0.95, result.Confidence)
	assert.Len(t, result.Suggestions, 2)
	assert.Equal(t, "suggestion1", result.Suggestions[0])
}

func TestAIClient_Analyze_ServerError(t *testing.T) {
	// Create mock server that returns error
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(`{"error": "Internal server error"}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	aiClient := clients.NewAIClient(pythonClient)

	ctx := context.Background()
	_, err := aiClient.Analyze(ctx, "Test text", "test-project")

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "AI analysis failed")
}
