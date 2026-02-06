package nats

import (
	"fmt"
	"log"
	"time"
)

const publishRetryBaseDelay = 100 * time.Millisecond

// PublishWithRetry publishes an event with retry logic for resilience
func PublishWithRetry(bridge *PythonBridge, eventType, projectID, entityID, entityType string, data map[string]interface{}, maxRetries int) error {
	var lastErr error
	for i := 0; i < maxRetries; i++ {
		err := bridge.PublishPythonEvent(eventType, projectID, entityID, entityType, data)
		if err == nil {
			return nil
		}
		lastErr = err
		log.Printf("Failed to publish event (attempt %d/%d): %v", i+1, maxRetries, err)
		time.Sleep(time.Duration(i+1) * publishRetryBaseDelay)
	}
	return fmt.Errorf("failed after %d retries: %w", maxRetries, lastErr)
}

// SafePublish publishes an event without failing the request if publishing fails
func SafePublish(bridge *PythonBridge, eventType, projectID, entityID, entityType string, data map[string]interface{}) {
	if bridge == nil {
		log.Printf("NATS bridge not available, skipping event publish: %s", eventType)
		return
	}

	go func() {
		if err := bridge.PublishPythonEvent(eventType, projectID, entityID, entityType, data); err != nil {
			log.Printf("Failed to publish %s event (non-blocking): %v", eventType, err)
		}
	}()
}

// SafePublishWithRetry combines SafePublish with retry logic
func SafePublishWithRetry(bridge *PythonBridge, eventType, projectID, entityID, entityType string, data map[string]interface{}, maxRetries int) {
	if bridge == nil {
		log.Printf("NATS bridge not available, skipping event publish: %s", eventType)
		return
	}

	go func() {
		if err := PublishWithRetry(bridge, eventType, projectID, entityID, entityType, data, maxRetries); err != nil {
			log.Printf("Failed to publish %s event after retries (non-blocking): %v", eventType, err)
		}
	}()
}
