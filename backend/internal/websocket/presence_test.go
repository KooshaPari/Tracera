package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	presenceStaleThreshold  = 10 * time.Minute
	presenceCleanupInterval = 5 * time.Minute
	presenceActivityDelay   = 10 * time.Millisecond
)

func TestNewPresenceTracker(t *testing.T) {
	pt := NewPresenceTracker()

	require.NotNil(t, pt)
	assert.NotNil(t, pt.clientPresence)
	assert.NotNil(t, pt.userClients)
	assert.NotNil(t, pt.projectUsers)
	assert.NotNil(t, pt.entityViewers)
	assert.NotNil(t, pt.entityEditors)
}

func TestPresenceJoin(t *testing.T) {
	pt := NewPresenceTracker()

	presence := pt.Join("client-1", "user-1", "project-1")

	require.NotNil(t, presence)
	assert.Equal(t, "user-1", presence.UserID)
	assert.Equal(t, "client-1", presence.ClientID)
	assert.Equal(t, "project-1", presence.ProjectID)
	assert.Equal(t, PresenceOnline, presence.Status)

	// Verify tracking
	assert.Len(t, pt.clientPresence, 1)
	assert.Len(t, pt.userClients["user-1"], 1)
	assert.True(t, pt.projectUsers["project-1"]["user-1"])
}

func TestPresenceLeave(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Leave("client-1")

	// Verify cleanup
	assert.Empty(t, pt.clientPresence)
	assert.Empty(t, pt.userClients)
	assert.Empty(t, pt.projectUsers["project-1"])
}

func TestPresenceMultipleClients(t *testing.T) {
	pt := NewPresenceTracker()

	// Same user, multiple clients (tabs/devices)
	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-1", "project-1")

	assert.Len(t, pt.clientPresence, 2)
	assert.Len(t, pt.userClients["user-1"], 2)

	// Leave one client
	pt.Leave("client-1")

	// User should still be in project (has another client)
	assert.Len(t, pt.clientPresence, 1)
	assert.True(t, pt.projectUsers["project-1"]["user-1"])

	// Leave last client
	pt.Leave("client-2")

	// User should be removed from project
	assert.Empty(t, pt.userClients)
	assert.Empty(t, pt.projectUsers["project-1"])
}

func TestUpdateStatus(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	originalTime := pt.clientPresence["client-1"].LastActivity

	time.Sleep(presenceActivityDelay)
	pt.UpdateStatus("client-1", PresenceIdle)

	presence := pt.clientPresence["client-1"]
	assert.Equal(t, PresenceIdle, presence.Status)
	assert.True(t, presence.LastActivity.After(originalTime))
}

func TestStartViewing(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.StartViewing("client-1", "entity-1", "item")

	presence := pt.clientPresence["client-1"]
	assert.Equal(t, PresenceViewing, presence.Status)
	assert.Equal(t, "entity-1", presence.EntityID)
	assert.Equal(t, "item", presence.EntityType)

	// Verify entity viewers tracking
	assert.Len(t, pt.entityViewers["entity-1"], 1)
}

func TestStartEditing(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.StartEditing("client-1", "entity-1", "item")

	presence := pt.clientPresence["client-1"]
	assert.Equal(t, PresenceEditing, presence.Status)
	assert.Equal(t, "entity-1", presence.EntityID)

	// Should be in both viewers and editors
	assert.Len(t, pt.entityViewers["entity-1"], 1)
	assert.Len(t, pt.entityEditors["entity-1"], 1)
}

func TestStopViewing(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.StartViewing("client-1", "entity-1", "item")
	pt.StopViewing("client-1")

	presence := pt.clientPresence["client-1"]
	assert.Equal(t, PresenceOnline, presence.Status)
	assert.Empty(t, presence.EntityID)

	// Should be removed from entity viewers
	assert.Empty(t, pt.entityViewers["entity-1"])
}

func TestSwitchEntity(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.StartViewing("client-1", "entity-1", "item")

	// Switch to viewing another entity
	pt.StartViewing("client-1", "entity-2", "item")

	// Should be removed from entity-1, added to entity-2
	assert.Empty(t, pt.entityViewers["entity-1"])
	assert.Len(t, pt.entityViewers["entity-2"], 1)

	presence := pt.clientPresence["client-1"]
	assert.Equal(t, "entity-2", presence.EntityID)
}

func TestHeartbeat(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	originalTime := pt.clientPresence["client-1"].LastSeen

	time.Sleep(presenceActivityDelay)
	pt.Heartbeat("client-1")

	presence := pt.clientPresence["client-1"]
	assert.True(t, presence.LastSeen.After(originalTime))
}

func TestGetProjectPresence(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.Join("client-3", "user-3", "project-2")

	presences := pt.GetProjectPresence("project-1")

	assert.Len(t, presences, 2)

	userIDs := []string{presences[0].UserID, presences[1].UserID}
	assert.Contains(t, userIDs, "user-1")
	assert.Contains(t, userIDs, "user-2")
}

func TestGetEntityViewers(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.Join("client-3", "user-3", "project-1")

	pt.StartViewing("client-1", "entity-1", "item")
	pt.StartViewing("client-2", "entity-1", "item")
	pt.StartViewing("client-3", "entity-2", "item")

	viewers := pt.GetEntityViewers("entity-1")

	assert.Len(t, viewers, 2)
}

func TestGetEntityEditors(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.Join("client-3", "user-3", "project-1")

	pt.StartViewing("client-1", "entity-1", "item")
	pt.StartEditing("client-2", "entity-1", "item")
	pt.StartEditing("client-3", "entity-2", "item")

	editors := pt.GetEntityEditors("entity-1")

	assert.Len(t, editors, 1)
	assert.Equal(t, "user-2", editors[0].UserID)
}

func TestGetUserPresence(t *testing.T) {
	pt := NewPresenceTracker()

	// Same user with multiple clients
	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-1", "project-1")

	presences := pt.GetUserPresence("user-1")

	assert.Len(t, presences, 2)
}

func TestCleanupStalePresence(t *testing.T) {
	pt := NewPresenceTracker()

	presence := pt.Join("client-1", "user-1", "project-1")
	presence.LastSeen = time.Now().Add(-presenceStaleThreshold)

	// Cleanup with 5 minute timeout
	removed := pt.CleanupStalePresence(presenceCleanupInterval)

	assert.Equal(t, 1, removed)
	assert.Empty(t, pt.clientPresence)
	assert.Empty(t, pt.userClients)
	assert.Empty(t, pt.projectUsers["project-1"])
}

func TestPresenceStats(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.Join("client-3", "user-3", "project-2")

	pt.StartViewing("client-1", "entity-1", "item")
	pt.StartEditing("client-2", "entity-2", "item")

	stats := pt.GetStats()

	assert.Equal(t, 3, stats["total_clients"])
	assert.Equal(t, 3, stats["total_users"])
	assert.Equal(t, 2, stats["total_projects"])
	assert.Equal(t, 2, stats["entities_being_viewed"])
	assert.Equal(t, 1, stats["entities_being_edited"])

	statusBreakdown, ok := stats["status_breakdown"].(map[PresenceStatus]int)
	require.True(t, ok)
	assert.Equal(t, 1, statusBreakdown[PresenceOnline])
	assert.Equal(t, 1, statusBreakdown[PresenceViewing])
	assert.Equal(t, 1, statusBreakdown[PresenceEditing])
}

func TestBroadcastPresenceUpdate(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")

	msg := pt.BroadcastPresenceUpdate("project-1")

	require.NotNil(t, msg)
	assert.Equal(t, "presence_update", msg.Type)
	assert.Equal(t, "project-1", msg.Data["project_id"])

	presence, ok := msg.Data["presence"].([]*PresenceActivity)
	require.True(t, ok)
	assert.Len(t, presence, 2)
}

func TestBroadcastEntityPresenceUpdate(t *testing.T) {
	pt := NewPresenceTracker()

	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")

	pt.StartViewing("client-1", "entity-1", "item")
	pt.StartEditing("client-2", "entity-1", "item")

	msg := pt.BroadcastEntityPresenceUpdate("entity-1")

	require.NotNil(t, msg)
	assert.Equal(t, "entity_presence_update", msg.Type)
	assert.Equal(t, "entity-1", msg.Data["entity_id"])

	viewers, ok := msg.Data["viewers"].([]*PresenceActivity)
	require.True(t, ok)
	editors, ok := msg.Data["editors"].([]*PresenceActivity)
	require.True(t, ok)

	assert.Len(t, viewers, 2)
	assert.Len(t, editors, 1)
}

func BenchmarkPresenceJoin(b *testing.B) {
	pt := NewPresenceTracker()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pt.Join(string(rune('a'+i)), string(rune('u'+i)), "project-1")
	}
}

func BenchmarkPresenceHeartbeat(b *testing.B) {
	pt := NewPresenceTracker()
	pt.Join("client-1", "user-1", "project-1")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pt.Heartbeat("client-1")
	}
}

func BenchmarkGetProjectPresence(b *testing.B) {
	pt := NewPresenceTracker()

	// Setup: create many presences
	for i := 0; i < 1000; i++ {
		pt.Join(string(rune('a'+i)), string(rune('u'+i)), "project-1")
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pt.GetProjectPresence("project-1")
	}
}
