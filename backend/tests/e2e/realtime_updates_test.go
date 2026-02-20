//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_ItemUpdate_RealtimeBroadcast tests real-time updates for item changes
func TestE2E_ItemUpdate_RealtimeBroadcast(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "realtime.user@test.com")

	// Connect WebSocket
	wsURL := "ws" + baseURL[4:] + "/api/v1/ws?token=" + url.QueryEscape(token)
	ws, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer func() {
		if err := ws.Close(); err != nil {
			// ignore error
		}
	}()

	// Subscribe to project updates
	subscribeMsg := map[string]interface{}{
		"type":       "subscribe",
		"project_id": projectID,
		"events":     []string{"item.created", "item.updated", "item.deleted"},
	}
	err = ws.WriteJSON(subscribeMsg)
	require.NoError(t, err)

	// Wait for subscription confirmation
	var subConfirm map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&subConfirm)
	require.NoError(t, err)
	assert.Equal(t, "subscribed", subConfirm["type"])

	// Create item via HTTP
	itemReq := map[string]interface{}{
		"project_id": projectID,
		"title":      "Realtime Test Item",
		"type":       "task",
	}
	itemBody, _ := json.Marshal(itemReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	resp.Body.Close()
	itemID := itemResp.ID

	// Receive WebSocket event for item creation
	var createEvent map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&createEvent)
	require.NoError(t, err)

	assert.Equal(t, "item.created", createEvent["event"])
	eventData := createEvent["data"].(map[string]interface{})
	assert.Equal(t, itemID, eventData["id"])
	assert.Equal(t, "Realtime Test Item", eventData["title"])

	// Update item
	updateReq := map[string]interface{}{
		"title":  "Updated Realtime Item",
		"status": "in_progress",
	}
	updateBody, _ := json.Marshal(updateReq)
	req, _ = http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/items/"+itemID, bytes.NewBuffer(updateBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	// Receive WebSocket event for item update
	var updateEvent map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&updateEvent)
	require.NoError(t, err)

	assert.Equal(t, "item.updated", updateEvent["event"])
	updateData := updateEvent["data"].(map[string]interface{})
	assert.Equal(t, itemID, updateData["id"])
	assert.Equal(t, "Updated Realtime Item", updateData["title"])

	// Delete item
	req, _ = http.NewRequestWithContext(context.Background(), "DELETE", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	// Receive WebSocket event for item deletion
	var deleteEvent map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&deleteEvent)
	require.NoError(t, err)

	assert.Equal(t, "item.deleted", deleteEvent["event"])
	deleteData := deleteEvent["data"].(map[string]interface{})
	assert.Equal(t, itemID, deleteData["id"])
}

// TestE2E_LinkCreation_RealtimeBroadcast tests real-time updates for link changes
func TestE2E_LinkCreation_RealtimeBroadcast(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "linkrt.user@test.com")

	// Create two items first
	itemIDs := make([]string, 2)
	for i := 0; i < 2; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Link Item %d", i),
			"type":       "task",
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[i] = itemResp.ID
	}

	// Connect WebSocket
	wsURL := "ws" + baseURL[4:] + "/api/v1/ws?token=" + url.QueryEscape(token)
	ws, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer func() {
		if err := ws.Close(); err != nil {
			// ignore error
		}
	}()

	// Subscribe to link events
	subscribeMsg := map[string]interface{}{
		"type":       "subscribe",
		"project_id": projectID,
		"events":     []string{"link.created", "link.deleted"},
	}
	err = ws.WriteJSON(subscribeMsg)
	require.NoError(t, err)

	// Wait for subscription confirmation
	var subConfirm map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&subConfirm)
	require.NoError(t, err)

	// Create link
	linkReq := map[string]interface{}{
		"source_id": itemIDs[0],
		"target_id": itemIDs[1],
		"type":      "blocks",
	}
	linkBody, _ := json.Marshal(linkReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var linkResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&linkResp)
	resp.Body.Close()
	linkID := linkResp.ID

	// Receive WebSocket event for link creation
	var createEvent map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&createEvent)
	require.NoError(t, err)

	assert.Equal(t, "link.created", createEvent["event"])
	eventData := createEvent["data"].(map[string]interface{})
	assert.Equal(t, linkID, eventData["id"])
	assert.Equal(t, itemIDs[0], eventData["source_id"])
	assert.Equal(t, itemIDs[1], eventData["target_id"])
}

// TestE2E_MultipleClients_EventPropagation tests event propagation to multiple clients
func TestE2E_MultipleClients_EventPropagation(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "multiws.user@test.com")

	// Connect 3 WebSocket clients
	wsClients := make([]*websocket.Conn, 3)
	for i := 0; i < 3; i++ {
		wsURL := "ws" + baseURL[4:] + "/api/v1/ws?token=" + url.QueryEscape(token)
		ws, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
		require.NoError(t, err)
		defer func() {
			if err := ws.Close(); err != nil {
				// ignore error
			}
		}()
		wsClients[i] = ws

		// Subscribe each client
		subscribeMsg := map[string]interface{}{
			"type":       "subscribe",
			"project_id": projectID,
			"events":     []string{"item.created"},
		}
		err = ws.WriteJSON(subscribeMsg)
		require.NoError(t, err)

		// Read subscription confirmation
		var subConfirm map[string]interface{}
		ws.SetReadDeadline(time.Now().Add(5 * time.Second))
		ws.ReadJSON(&subConfirm)
	}

	// Create item
	itemReq := map[string]interface{}{
		"project_id": projectID,
		"title":      "Multi-client broadcast test",
		"type":       "task",
	}
	itemBody, _ := json.Marshal(itemReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	resp.Body.Close()
	itemID := itemResp.ID

	// All clients should receive the event
	for i, ws := range wsClients {
		var event map[string]interface{}
		ws.SetReadDeadline(time.Now().Add(5 * time.Second))
		err = ws.ReadJSON(&event)
		require.NoError(t, err, "Client %d should receive event", i)

		assert.Equal(t, "item.created", event["event"])
		eventData := event["data"].(map[string]interface{})
		assert.Equal(t, itemID, eventData["id"])
	}
}

// TestE2E_WebSocket_Reconnection tests WebSocket reconnection handling
func TestE2E_WebSocket_Reconnection(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "reconnect.user@test.com")

	// Connect WebSocket
	wsURL := "ws" + baseURL[4:] + "/api/v1/ws?token=" + url.QueryEscape(token)
	ws, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)

	// Subscribe
	subscribeMsg := map[string]interface{}{
		"type":       "subscribe",
		"project_id": projectID,
		"events":     []string{"item.created"},
	}
	err = ws.WriteJSON(subscribeMsg)
	require.NoError(t, err)

	var subConfirm map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	ws.ReadJSON(&subConfirm)

	// Create item - should receive event
	itemReq := map[string]interface{}{
		"project_id": projectID,
		"title":      "Before disconnect",
		"type":       "task",
	}
	itemBody, _ := json.Marshal(itemReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	var event1 map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&event1)
	require.NoError(t, err)
	assert.Equal(t, "item.created", event1["event"])

	// Close connection
	_ = ws.Close()
	time.Sleep(1 * time.Second)

	// Reconnect
	ws, _, err = websocket.DefaultDialer.Dial(wsURL, nil)
	require.NoError(t, err)
	defer func() {
		if err := ws.Close(); err != nil {
			// ignore error
		}
	}()

	// Resubscribe
	err = ws.WriteJSON(subscribeMsg)
	require.NoError(t, err)

	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	ws.ReadJSON(&subConfirm)

	// Create another item - should receive event on new connection
	itemReq = map[string]interface{}{
		"project_id": projectID,
		"title":      "After reconnect",
		"type":       "task",
	}
	itemBody, _ = json.Marshal(itemReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	var event2 map[string]interface{}
	ws.SetReadDeadline(time.Now().Add(5 * time.Second))
	err = ws.ReadJSON(&event2)
	require.NoError(t, err)
	assert.Equal(t, "item.created", event2["event"])

	eventData := event2["data"].(map[string]interface{})
	assert.Equal(t, "After reconnect", eventData["title"])
}
