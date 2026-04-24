package nats

import (
	"fmt"
	"log/slog"
	"time"
)

const publishRetryBaseDelay = 100 * time.Millisecond

// PublishWithRetry publishes an event with retry logic for resilience
func PublishWithRetry(
	bridge *PythonBridge, eventType, projectID, entityID, entityType string,
	data map[string]interface{}, maxRetries int,
) error {
	var lastErr error
	for i := 0; i < maxRetries; i++ {
		err := bridge.PublishPythonEvent(eventType, projectID, entityID, entityType, data)
		if err == nil {
			return nil
		}
		lastErr = err
		slog.Error("Failed to publish event (attempt / )", "error", i+1, "value", maxRetries, "error", err)
		time.Sleep(time.Duration(i+1) * publishRetryBaseDelay)
	}
	return fmt.Errorf("failed after %d retries: %w", maxRetries, lastErr)
}

// SafePublish publishes an event without failing the request if publishing fails
func SafePublish(bridge *PythonBridge, eventType, projectID, entityID, entityType string, data map[string]interface{}) {
	if bridge == nil {
		slog.Warn("NATS bridge not available, skipping event publish", "id", eventType)
		return
	}

	go func() {
		if err := bridge.PublishPythonEvent(eventType, projectID, entityID, entityType, data); err != nil {
			slog.Error("Failed to publish event (non-blocking)", "error", eventType, "error", err)
		}
	}()
}

// SafePublishWithRetry combines SafePublish with retry logic
func SafePublishWithRetry(
	bridge *PythonBridge, eventType, projectID, entityID, entityType string,
	data map[string]interface{}, maxRetries int,
) {
	if bridge == nil {
		slog.Warn("NATS bridge not available, skipping event publish", "id", eventType)
		return
	}

	go func() {
		if err := PublishWithRetry(bridge, eventType, projectID, entityID, entityType, data, maxRetries); err != nil {
			slog.Error("Failed to publish event after retries (non-blocking)", "error", eventType, "error", err)
		}
	}()
}
