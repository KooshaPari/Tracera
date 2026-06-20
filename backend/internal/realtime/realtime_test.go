//go:build !integration

package realtime

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestEventStruct(t *testing.T) {
	event := Event{
		Type:      "INSERT",
		Table:     "items",
		Schema:    "public",
		Record:    map[string]interface{}{"id": "123", "title": "Test"},
		OldRecord: nil,
		Timestamp: 1700000000,
	}

	assert.Equal(t, "INSERT", event.Type)
	assert.Equal(t, "items", event.Table)
	assert.Equal(t, "public", event.Schema)
	assert.Equal(t, "123", event.Record["id"])
	assert.Nil(t, event.OldRecord)
	assert.Equal(t, int64(1700000000), event.Timestamp)
}

func TestEventStruct_Update(t *testing.T) {
	event := Event{
		Type:      "UPDATE",
		Table:     "items",
		Schema:    "public",
		Record:    map[string]interface{}{"id": "123", "title": "Updated"},
		OldRecord: map[string]interface{}{"id": "123", "title": "Old"},
		Timestamp: 1700000001,
	}

	assert.Equal(t, "UPDATE", event.Type)
	assert.Equal(t, "Updated", event.Record["title"])
	assert.Equal(t, "Old", event.OldRecord["title"])
}

func TestEventStruct_Delete(t *testing.T) {
	event := Event{
		Type:      "DELETE",
		Table:     "links",
		Schema:    "public",
		OldRecord: map[string]interface{}{"id": "456"},
	}

	assert.Equal(t, "DELETE", event.Type)
	assert.Equal(t, "links", event.Table)
	assert.Nil(t, event.Record)
	assert.NotNil(t, event.OldRecord)
}

// TestSubscriberInterface verifies the interface is properly defined
func TestSubscriberInterface(t *testing.T) {
	var _ Subscriber = (*NATSRealtimeAdapter)(nil)
}

// TestPublisherInterface verifies the interface is properly defined
func TestPublisherInterface(t *testing.T) {
	var _ Publisher = (*NATSRealtimeAdapter)(nil)
}

// TestBroadcasterInterface verifies the interface is properly defined
func TestBroadcasterInterface(t *testing.T) {
	var _ Broadcaster = (*NATSRealtimeAdapter)(nil)
}

func TestNewNATSRealtimeAdapter_NilConn(t *testing.T) {
	// Should not panic with nil conn (it's up to caller)
	adapter := NewNATSRealtimeAdapter(nil)
	assert.NotNil(t, adapter)
	assert.NotNil(t, adapter.subscriptions)
	assert.Empty(t, adapter.subscriptions)
}
