package events

import (
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func applyItemStringField(data map[string]interface{}, key string, apply func(string)) {
	value, ok := data[key].(string)
	if !ok {
		return
	}
	apply(value)
}

func applyItemPriorityField(item *models.Item, data map[string]interface{}, key string) {
	value, ok := data[key]
	if !ok {
		return
	}
	item.Priority = priorityFromData(value)
}

func applyCreatedOrUpdated(item *models.Item, event *Event) {
	applyItemStringField(event.Data, "title", func(value string) {
		item.Title = value
	})
	applyItemStringField(event.Data, "description", func(value string) {
		item.Description = value
	})
	applyItemStringField(event.Data, "type", func(value string) {
		item.Type = value
	})
	applyItemStringField(event.Data, "status", func(value string) {
		item.Status = value
	})
	applyItemPriorityField(item, event.Data, "priority")
	item.ProjectID = event.ProjectID
	item.CreatedAt = event.CreatedAt
}

func applyStatusChange(item *models.Item, event *Event) {
	applyItemStringField(event.Data, "new_status", func(value string) {
		item.Status = value
	})
}

func applyPriorityChange(item *models.Item, event *Event) {
	applyItemPriorityField(item, event.Data, "new_priority")
}

func applyDeleted(item *models.Item, event *Event) {
	now := event.CreatedAt
	item.DeletedAt = &now
}

// ReconstructItemFromEvents rebuilds an item from its event history
func ReconstructItemFromEvents(entityID string, store EventStore) (*models.Item, error) {
	events, err := store.GetByEntityID(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	if len(events) == 0 {
		return nil, fmt.Errorf("no events found for entity %s", entityID)
	}

	item := &models.Item{
		ID: entityID,
	}

	for _, event := range events {
		switch event.EventType {
		case EventTypeCreated, EventTypeUpdated:
			applyCreatedOrUpdated(item, event)

		case EventTypeItemStatusChanged:
			applyStatusChange(item, event)

		case EventTypeItemPriorityChanged:
			applyPriorityChange(item, event)

		case EventTypeDeleted:
			applyDeleted(item, event)
		case EventTypeLinkCreated,
			EventTypeLinkDeleted,
			EventTypeAgentStarted,
			EventTypeAgentStopped,
			EventTypeAgentActivity,
			EventTypeAgentError,
			EventTypeSnapshot,
			EventTypeRollback:
			// Not applicable for item reconstruction.
		}
	}

	return item, nil
}
