package handlers

import (
	"context"
	"log"
)

// publishAgentEvent is test-only to preserve existing test helpers without
// requiring runtime usage in production builds.
func (h *AgentHandler) publishAgentEvent(_ context.Context, eventType string, agentID string, projectID string, agent interface{}) {
	if h.publisher == nil {
		return
	}

	if err := h.publisher.PublishAgentEvent(eventType, projectID, agentID, agent); err != nil {
		log.Printf("Failed to publish agent event: %v", err)
	}
}
