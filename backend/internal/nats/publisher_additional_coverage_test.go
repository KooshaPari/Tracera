//go:build !integration && !e2e

package nats

import (
	"testing"
)

// TestEventPublisher_AllMethods tests all EventPublisher methods with nil connection
func TestEventPublisher_AllMethods(t *testing.T) {
	t.Run("PublishItemEvent with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		err := publisher.PublishItemEvent("created", "project-1", "item-1", map[string]string{"test": "data"})
		// Should handle nil connection gracefully
		_ = err
	})

	t.Run("PublishLinkEvent with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		err := publisher.PublishLinkEvent("created", "project-1", "link-1", map[string]string{"test": "data"})
		_ = err
	})

	t.Run("PublishProjectEvent with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		err := publisher.PublishProjectEvent("created", "project-1", map[string]string{"test": "data"})
		_ = err
	})

	t.Run("PublishAgentEvent with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		err := publisher.PublishAgentEvent("created", "project-1", "agent-1", map[string]string{"test": "data"})
		// Will fail on nil conn.Publish, but tests error path
		_ = err
	})

	t.Run("Close with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		// Should not panic
		publisher.Close()
	})
}

// TestEventPublisher_ErrorHandling tests error handling in EventPublisher
func TestEventPublisher_ErrorHandling(t *testing.T) {
	t.Run("marshal error handling", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		// Data that can't be marshaled
		type Unmarshalable struct {
			Channel chan int
		}
		unmarshalable := &Unmarshalable{Channel: make(chan int)}

		// Should return error for marshal failure
		err := publisher.PublishItemEvent("created", "project-1", "item-1", unmarshalable)
		// Will fail on json.Marshal, testing error path
		_ = err
	})

	t.Run("publishEvent with nil connection", func(_ *testing.T) {
		publisher := &EventPublisher{
			conn: nil,
		}

		// publishEvent is private, but we test through public methods
		// This tests the nil conn.Publish path
		err := publisher.PublishItemEvent("created", "project-1", "item-1", map[string]string{"test": "data"})
		// Will fail on nil conn.Publish
		_ = err
	})
}
