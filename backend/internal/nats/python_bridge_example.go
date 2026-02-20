package nats

import (
	"log/slog"
	"os"

	natslib "github.com/nats-io/nats.go"
)

// ExamplePythonBridgeUsage demonstrates how to integrate the Python bridge in a Go service
func ExamplePythonBridgeUsage() {
	natsClient, err := initNATSClient()
	if err != nil {
		slog.Error("Failed to connect to NATS", "error", err)
		return
	}
	defer closeWithLog("NATS client", natsClient.Close)

	bridge, err := NewPythonBridge(natsClient.GetConnection())
	if err != nil {
		slog.Error("Failed to create Python bridge", "error", err)
		return
	}
	defer closeWithLog("Python bridge", bridge.Close)

	if err := subscribeToPythonBridge(bridge); err != nil {
		slog.Error("Failed to subscribe to Python events", "error", err)
		return
	}

	publishExampleEvents(bridge)

	// Keep the service running
	slog.Info("Python bridge initialized successfully")
	select {} // Block forever (in real service, use proper shutdown handling)
}

func initNATSClient() (*Client, error) {
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = natslib.DefaultURL
	}

	return NewClient(natsURL, os.Getenv("NATS_CREDS_PATH"))
}

func closeWithLog(name string, closeFn func() error) {
	if err := closeFn(); err != nil {
		slog.Error("Failed to close", "error", name, "error", err)
	}
}

func subscribeToPythonBridge(bridge *PythonBridge) error {
	if err := bridge.SubscribeToPythonEvents(handlePythonEvent); err != nil {
		return err
	}

	return bridge.SubscribeToEventType(SubjectSpecCreated, handleSpecCreated)
}

func handlePythonEvent(event *BridgeEvent) {
	slog.Info("Received Python event for", "detail", event.Type, "id", event.EntityID)

	switch event.Type {
	case SubjectSpecCreated:
		handleSpecCreated(event)
	case SubjectAIAnalysisComplete:
		handleAIAnalysisComplete(event)
	case SubjectExecutionCompleted:
		handleExecutionCompleted(event)
	default:
		slog.Info("Unhandled event type", "type", event.Type)
	}
}

func publishExampleEvents(bridge *PythonBridge) {
	if err := bridge.PublishItemEvent(
		SubjectItemCreated,
		"550e8400-e29b-41d4-a716-446655440000",
		"660e8400-e29b-41d4-a716-446655440001",
		map[string]interface{}{
			"title":    "New Feature Request",
			"type":     "feature",
			"status":   "open",
			"priority": "high",
		},
	); err != nil {
		slog.Error("Failed to publish item event", "error", err)
	}

	if err := bridge.PublishLinkEvent(
		SubjectLinkCreated,
		"550e8400-e29b-41d4-a716-446655440000",
		"770e8400-e29b-41d4-a716-446655440002",
		map[string]interface{}{
			"source_id": "660e8400-e29b-41d4-a716-446655440001",
			"target_id": "880e8400-e29b-41d4-a716-446655440003",
			"type":      "implements",
		},
	); err != nil {
		slog.Error("Failed to publish link event", "error", err)
	}
}

// Event handlers

func handleSpecCreated(event *BridgeEvent) {
	slog.Info("Handling spec.created", "id", event.EntityID)

	// Extract spec data
	title, ok := event.Data["title"].(string)
	if !ok {
		title = ""
	}
	specType, ok := event.Data["type"].(string)
	if !ok {
		specType = ""
	}

	slog.Info("New specification (type )", "detail", title, "type", specType)

	// Business logic:
	// - Update traceability graph in Neo4j
	// - Trigger impact analysis
	// - Update search index
	// - Send notifications
}

func handleAIAnalysisComplete(event *BridgeEvent) {
	slog.Info("Handling ai.analysis.complete", "id", event.EntityID)

	// Extract analysis data
	specID, ok := event.Data["spec_id"].(string)
	if !ok {
		specID = ""
	}
	confidence, ok := event.Data["confidence"].(float64)
	if !ok {
		confidence = 0
	}

	slog.Info("AI analysis complete for spec (confidence )", "id", specID, "id", confidence)

	// Business logic:
	// - Update item metadata with AI insights
	// - Create traceability links based on analysis
	// - Trigger follow-up workflows
}

func handleExecutionCompleted(event *BridgeEvent) {
	slog.Info("Handling execution.completed", "id", event.EntityID)

	// Extract execution data
	status, ok := event.Data["status"].(string)
	if !ok {
		status = ""
	}
	testCount, ok := event.Data["test_count"].(float64)
	if !ok {
		testCount = 0
	}

	slog.Info("Test execution completed ( tests)", "id", status, "value", int(testCount))

	// Business logic:
	// - Update test coverage metrics
	// - Update item status based on test results
	// - Trigger CI/CD pipeline steps
}

// IntegrateWithService shows how to integrate the bridge into an existing service
func IntegrateWithService() (*PythonBridge, error) {
	// Get NATS configuration from environment
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = natslib.DefaultURL
	}

	credsPath := os.Getenv("NATS_CREDS_PATH")

	// Connect to NATS
	natsClient, err := NewClient(natsURL, credsPath)
	if err != nil {
		return nil, err
	}

	// Create bridge
	bridge, err := NewPythonBridge(natsClient.GetConnection())
	if err != nil {
		if closeErr := natsClient.Close(); closeErr != nil {
			slog.Error("Failed to close NATS client", "error", closeErr)
		}
		return nil, err
	}

	// Set up subscriptions
	setupSubscriptions(bridge)

	slog.Info("Python bridge initialized at", "id", natsURL)
	return bridge, nil
}

func setupSubscriptions(bridge *PythonBridge) {
	// Subscribe to all Python events for logging/monitoring
	if err := bridge.SubscribeToPythonEvents(func(event *BridgeEvent) {
		slog.Info("[EVENT] /", "detail", event.Type, "detail", event.EntityType, "id", event.EntityID)
	}); err != nil {
		slog.Error("Failed to subscribe to Python events", "error", err)
	}

	// Subscribe to specific events
	eventHandlers := map[string]func(*BridgeEvent){
		SubjectSpecCreated:        handleSpecCreated,
		SubjectSpecUpdated:        handleSpecUpdated,
		SubjectSpecDeleted:        handleSpecDeleted,
		SubjectAIAnalysisComplete: handleAIAnalysisComplete,
		SubjectExecutionCompleted: handleExecutionCompleted,
		SubjectExecutionFailed:    handleExecutionFailed,
		SubjectWorkflowCompleted:  handleWorkflowCompleted,
	}

	for eventType, handler := range eventHandlers {
		if err := bridge.SubscribeToEventType(eventType, handler); err != nil {
			slog.Error("Warning: Failed to subscribe to", "error", eventType, "error", err)
		}
	}
}

// Placeholder handlers (implement based on your business logic)

func handleSpecUpdated(event *BridgeEvent) {
	slog.Info("Spec updated", "id", event.EntityID)
}

func handleSpecDeleted(event *BridgeEvent) {
	slog.Info("Spec deleted", "id", event.EntityID)
}

func handleExecutionFailed(event *BridgeEvent) {
	slog.Error("Execution failed", "error", event.EntityID)
}

func handleWorkflowCompleted(event *BridgeEvent) {
	slog.Info("Workflow completed", "id", event.EntityID)
}
