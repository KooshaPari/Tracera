package nats

import (
	"log"
	"os"

	natslib "github.com/nats-io/nats.go"
)

// ExamplePythonBridgeUsage demonstrates how to integrate the Python bridge in a Go service
func ExamplePythonBridgeUsage() {
	natsClient, err := initNATSClient()
	if err != nil {
		log.Printf("Failed to connect to NATS: %v", err)
		return
	}
	defer closeWithLog("NATS client", natsClient.Close)

	bridge, err := NewPythonBridge(natsClient.GetConnection())
	if err != nil {
		log.Printf("Failed to create Python bridge: %v", err)
		return
	}
	defer closeWithLog("Python bridge", bridge.Close)

	if err := subscribeToPythonBridge(bridge); err != nil {
		log.Printf("Failed to subscribe to Python events: %v", err)
		return
	}

	publishExampleEvents(bridge)

	// Keep the service running
	log.Println("Python bridge initialized successfully")
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
		log.Printf("Failed to close %s: %v", name, err)
	}
}

func subscribeToPythonBridge(bridge *PythonBridge) error {
	if err := bridge.SubscribeToPythonEvents(handlePythonEvent); err != nil {
		return err
	}

	return bridge.SubscribeToEventType(SubjectSpecCreated, handleSpecCreated)
}

func handlePythonEvent(event *BridgeEvent) {
	log.Printf("Received Python event: %s for %s", event.Type, event.EntityID)

	switch event.Type {
	case SubjectSpecCreated:
		handleSpecCreated(event)
	case SubjectAIAnalysisComplete:
		handleAIAnalysisComplete(event)
	case SubjectExecutionCompleted:
		handleExecutionCompleted(event)
	default:
		log.Printf("Unhandled event type: %s", event.Type)
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
		log.Printf("Failed to publish item event: %v", err)
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
		log.Printf("Failed to publish link event: %v", err)
	}
}

// Event handlers

func handleSpecCreated(event *BridgeEvent) {
	log.Printf("Handling spec.created: %s", event.EntityID)

	// Extract spec data
	title, _ := event.Data["title"].(string)
	specType, _ := event.Data["type"].(string)

	log.Printf("New specification: %s (type: %s)", title, specType)

	// Business logic:
	// - Update traceability graph in Neo4j
	// - Trigger impact analysis
	// - Update search index
	// - Send notifications
}

func handleAIAnalysisComplete(event *BridgeEvent) {
	log.Printf("Handling ai.analysis.complete: %s", event.EntityID)

	// Extract analysis data
	specID, _ := event.Data["spec_id"].(string)
	confidence, _ := event.Data["confidence"].(float64)

	log.Printf("AI analysis complete for spec %s (confidence: %.2f)", specID, confidence)

	// Business logic:
	// - Update item metadata with AI insights
	// - Create traceability links based on analysis
	// - Trigger follow-up workflows
}

func handleExecutionCompleted(event *BridgeEvent) {
	log.Printf("Handling execution.completed: %s", event.EntityID)

	// Extract execution data
	status, _ := event.Data["status"].(string)
	testCount, _ := event.Data["test_count"].(float64)

	log.Printf("Test execution completed: %s (%d tests)", status, int(testCount))

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
			log.Printf("Failed to close NATS client: %v", closeErr)
		}
		return nil, err
	}

	// Set up subscriptions
	setupSubscriptions(bridge)

	log.Printf("Python bridge initialized at %s", natsURL)
	return bridge, nil
}

func setupSubscriptions(bridge *PythonBridge) {
	// Subscribe to all Python events for logging/monitoring
	if err := bridge.SubscribeToPythonEvents(func(event *BridgeEvent) {
		log.Printf("[EVENT] %s: %s/%s", event.Type, event.EntityType, event.EntityID)
	}); err != nil {
		log.Printf("Failed to subscribe to Python events: %v", err)
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
			log.Printf("Warning: Failed to subscribe to %s: %v", eventType, err)
		}
	}
}

// Placeholder handlers (implement based on your business logic)

func handleSpecUpdated(event *BridgeEvent) {
	log.Printf("Spec updated: %s", event.EntityID)
}

func handleSpecDeleted(event *BridgeEvent) {
	log.Printf("Spec deleted: %s", event.EntityID)
}

func handleExecutionFailed(event *BridgeEvent) {
	log.Printf("Execution failed: %s", event.EntityID)
}

func handleWorkflowCompleted(event *BridgeEvent) {
	log.Printf("Workflow completed: %s", event.EntityID)
}
