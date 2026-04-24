package events

import (
	"strconv"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// priorityFromData converts event data (string, int32, float64) to int32 for models.Item.Priority
func priorityFromData(v interface{}) models.Priority {
	switch value := v.(type) {
	case int32:
		return models.Priority(value)
	case models.Priority:
		return value
	case float64:
		return models.Priority(int32(value))
	case string:
		if i, err := strconv.ParseInt(value, 10, 32); err == nil {
			return models.Priority(int32(i))
		}
		switch value {
		case "low":
			return models.PriorityLow
		case "medium":
			return models.PriorityMedium
		case "high":
			return models.PriorityHigh
		case "critical":
			return models.PriorityCritical
		}
		return 0
	}
	return 0
}

// GenerateCorrelationID creates a new correlation ID for tracing related operations
func GenerateCorrelationID() string {
	return uuid.New().String()
}
