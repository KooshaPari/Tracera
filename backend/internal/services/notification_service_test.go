package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type fakeNotificationEventBus struct {
	published      []*NotificationEvent
	handlers       []func(*NotificationEvent)
	unsubscribeHit bool
}

func (b *fakeNotificationEventBus) PublishNotification(
	_ context.Context,
	_ string,
	event *NotificationEvent,
) error {
	b.published = append(b.published, event)
	return nil
}

func (b *fakeNotificationEventBus) SubscribeNotifications(
	_ context.Context,
	handler func(*NotificationEvent),
) (func() error, error) {
	b.handlers = append(b.handlers, handler)
	return func() error {
		b.unsubscribeHit = true
		return nil
	}, nil
}

func TestNotificationServiceLocalFallbackBroadcast(t *testing.T) {
	service := NewNotificationService(nil, nil)
	_, events := service.Subscribe("user-1")

	event := &NotificationEvent{Type: "read", UserID: "user-1", Timestamp: time.Now().Unix()}
	require.NoError(t, service.broadcastEvent(context.Background(), "user-1", event))

	select {
	case received := <-events:
		assert.Equal(t, event, received)
	case <-time.After(100 * time.Millisecond):
		t.Fatal("timeout waiting for local notification event")
	}
}

func TestNotificationServicePublishesThroughEventBus(t *testing.T) {
	bus := &fakeNotificationEventBus{}
	service := NewNotificationService(nil, bus)

	event := &NotificationEvent{Type: "delete", UserID: "user-1", Timestamp: time.Now().Unix()}
	require.NoError(t, service.broadcastEvent(context.Background(), "user-1", event))

	require.Len(t, bus.published, 1)
	assert.Equal(t, event, bus.published[0])
}

func TestNotificationServiceEventBusListenerFanout(t *testing.T) {
	bus := &fakeNotificationEventBus{}
	service := NewNotificationService(nil, bus)
	_, events := service.Subscribe("user-1")

	require.Len(t, bus.handlers, 1)
	event := &NotificationEvent{Type: "notification", UserID: "user-1", Timestamp: time.Now().Unix()}
	bus.handlers[0](event)

	select {
	case received := <-events:
		assert.Equal(t, event, received)
	case <-time.After(100 * time.Millisecond):
		t.Fatal("timeout waiting for event-bus notification event")
	}
}

func TestNotificationServiceCloseUnsubscribesEventBus(t *testing.T) {
	bus := &fakeNotificationEventBus{}
	service := NewNotificationService(nil, bus)

	require.NoError(t, service.Close())
	assert.True(t, bus.unsubscribeHit)
}
