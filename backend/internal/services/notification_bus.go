package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"

	"github.com/kooshapari/tracertm-backend/internal/nats"
)

type natsNotificationEventBus struct {
	publisher *nats.EventPublisher
}

func newNotificationEventBus(publisher *nats.EventPublisher) notificationEventBus {
	if publisher == nil {
		return nil
	}
	return &natsNotificationEventBus{publisher: publisher}
}

func (b *natsNotificationEventBus) PublishNotification(
	_ context.Context,
	userID string,
	event *NotificationEvent,
) error {
	if event == nil {
		return fmt.Errorf("notification event is required")
	}
	return b.publisher.PublishNotification(userID, event)
}

func (b *natsNotificationEventBus) SubscribeNotifications(
	_ context.Context,
	handler func(*NotificationEvent),
) (func() error, error) {
	return b.publisher.SubscribeNotifications(func(_ string, data []byte) {
		var event NotificationEvent
		if err := json.Unmarshal(data, &event); err != nil {
			slog.Error("failed to unmarshal NATS notification event", "error", err)
			return
		}
		handler(&event)
	})
}
