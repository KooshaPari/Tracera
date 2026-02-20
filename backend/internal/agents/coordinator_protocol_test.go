//go:build !integration && !e2e

package agents

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestProtocolMessageSerialization(t *testing.T) {
	protocol := NewProtocol()

	req := &RegisterRequest{
		Name:      "test-agent",
		ProjectID: uuid.New().String(),
		Capabilities: []AgentCapability{
			{Name: "test", Version: "1.0"},
		},
		Metadata: nil,
	}

	msg := protocol.CreateRegisterMessage(req)
	assert.Equal(t, MsgTypeRegister, msg.Type)
	assert.NotNil(t, msg.Payload)

	serialized, err := protocol.SerializeMessage(msg)
	require.NoError(t, err)
	assert.NotEmpty(t, serialized)
}

func TestProtocolMessageDeserialization(t *testing.T) {
	protocol := NewProtocol()

	original := &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   uuid.New().String(),
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"status": "idle",
		},
	}

	serialized, err := protocol.SerializeMessage(original)
	require.NoError(t, err)

	parsed, err := protocol.ParseMessage(serialized)
	require.NoError(t, err)
	assert.Equal(t, original.Type, parsed.Type)
	assert.Equal(t, original.AgentID, parsed.AgentID)
}

func TestProtocolHandshake(t *testing.T) {
	protocol := NewProtocol()

	registerMsg := protocol.CreateRegisterMessage(&RegisterRequest{
		Name:         "test-agent",
		ProjectID:    uuid.New().String(),
		Capabilities: nil,
		Metadata:     nil,
	})

	err := protocol.ValidateMessage(registerMsg)
	require.NoError(t, err)

	ackMsg := protocol.CreateAckMessage("success", "Agent registered")
	assert.Equal(t, MsgTypeAck, ackMsg.Type)
}
