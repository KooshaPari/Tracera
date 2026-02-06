package agents

import (
	"encoding/json"
	"time"
)

// MessageType represents the type of message in the agent protocol
type MessageType string

const (
	// MsgTypeRegister is sent by agent to register with coordinator.
	MsgTypeRegister MessageType = "register"
	// MsgTypeHeartbeat is sent by agent to report liveness.
	MsgTypeHeartbeat MessageType = "heartbeat"
	// MsgTypeTaskRequest is sent by an agent to request a task.
	MsgTypeTaskRequest MessageType = "task_request"
	// MsgTypeTaskResult is sent by an agent with task results.
	MsgTypeTaskResult MessageType = "task_result"
	// MsgTypeTaskError is sent by an agent to report task failure.
	MsgTypeTaskError MessageType = "task_error"
	// MsgTypeUnregister is sent by an agent to unregister.
	MsgTypeUnregister MessageType = "unregister"

	// MsgTypeAck is sent by coordinator to acknowledge receipt.
	MsgTypeAck MessageType = "ack"
	// MsgTypeTaskAssigned indicates a task assignment.
	MsgTypeTaskAssigned MessageType = "task_assigned"
	// MsgTypeNoTask indicates no tasks are available.
	MsgTypeNoTask MessageType = "no_task"
	// MsgTypeError indicates a protocol error.
	MsgTypeError MessageType = "error"
	// MsgTypeShutdown instructs an agent to shutdown.
	MsgTypeShutdown MessageType = "shutdown"
)

// Message represents a protocol message
type Message struct {
	Type      MessageType            `json:"type"`
	AgentID   string                 `json:"agent_id,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
	Payload   map[string]interface{} `json:"payload,omitempty"`
	Error     string                 `json:"error,omitempty"`
}

// RegisterRequest is sent by an agent to register with the coordinator
type RegisterRequest struct {
	Name         string                 `json:"name"`
	ProjectID    string                 `json:"project_id"`
	Capabilities []AgentCapability      `json:"capabilities"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
}

// RegisterResponse is sent by the coordinator in response to registration
type RegisterResponse struct {
	AgentID string    `json:"agent_id"`
	Status  string    `json:"status"`
	Message string    `json:"message"`
	Time    time.Time `json:"time"`
}

// HeartbeatRequest is sent by an agent to indicate it's still alive
type HeartbeatRequest struct {
	AgentID string        `json:"agent_id"`
	Status  AgentStatus   `json:"status"`
	Metrics *AgentMetrics `json:"metrics,omitempty"`
}

// HeartbeatResponse is sent by the coordinator in response to heartbeat
type HeartbeatResponse struct {
	Status  string    `json:"status"`
	Time    time.Time `json:"time"`
	Message string    `json:"message,omitempty"`
}

// TaskRequest is sent by an agent to request a new task
type TaskRequest struct {
	AgentID string   `json:"agent_id"`
	Tags    []string `json:"tags,omitempty"` // Optional: filter tasks by tags
}

// TaskResponse is sent by the coordinator with a task assignment
type TaskResponse struct {
	Task    *Task  `json:"task,omitempty"`
	Status  string `json:"status"`
	Message string `json:"message,omitempty"`
}

// TaskResultRequest is sent by an agent with task results
type TaskResultRequest struct {
	AgentID string      `json:"agent_id"`
	TaskID  string      `json:"task_id"`
	Result  *TaskResult `json:"result"`
}

// TaskResultResponse is sent by the coordinator acknowledging task completion
type TaskResultResponse struct {
	Status  string    `json:"status"`
	Message string    `json:"message,omitempty"`
	Time    time.Time `json:"time"`
}

// TaskErrorRequest is sent by an agent when a task fails
type TaskErrorRequest struct {
	AgentID      string    `json:"agent_id"`
	TaskID       string    `json:"task_id"`
	ErrorMessage string    `json:"error_message"`
	ErrorCode    string    `json:"error_code,omitempty"`
	Retryable    bool      `json:"retryable"`
	Timestamp    time.Time `json:"timestamp"`
}

// TaskErrorResponse is sent by the coordinator acknowledging task failure
type TaskErrorResponse struct {
	Status     string `json:"status"`
	Message    string `json:"message,omitempty"`
	WillRetry  bool   `json:"will_retry"`
	RetryCount int    `json:"retry_count,omitempty"`
}

// AgentMetrics contains performance metrics from an agent
type AgentMetrics struct {
	CPUUsage        float64 `json:"cpu_usage"`
	MemoryUsage     float64 `json:"memory_usage"`
	TasksCompleted  int     `json:"tasks_completed"`
	TasksFailed     int     `json:"tasks_failed"`
	AverageTaskTime float64 `json:"average_task_time"` // in seconds
}

// Protocol provides helper methods for creating protocol messages
type Protocol struct{}

// NewProtocol creates a new protocol handler
func NewProtocol() *Protocol {
	return &Protocol{}
}

// CreateRegisterMessage creates a registration message
func (p *Protocol) CreateRegisterMessage(req *RegisterRequest) *Message {
	payload := map[string]interface{}{
		"name":         req.Name,
		"project_id":   req.ProjectID,
		"capabilities": req.Capabilities,
		"metadata":     req.Metadata,
	}

	return &Message{
		Type:      MsgTypeRegister,
		Timestamp: time.Now(),
		Payload:   payload,
	}
}

// CreateHeartbeatMessage creates a heartbeat message
func (p *Protocol) CreateHeartbeatMessage(req *HeartbeatRequest) *Message {
	payload := map[string]interface{}{
		"agent_id": req.AgentID,
		"status":   req.Status,
	}

	if req.Metrics != nil {
		payload["metrics"] = req.Metrics
	}

	return &Message{
		Type:      MsgTypeHeartbeat,
		AgentID:   req.AgentID,
		Timestamp: time.Now(),
		Payload:   payload,
	}
}

// CreateTaskRequestMessage creates a task request message
func (p *Protocol) CreateTaskRequestMessage(req *TaskRequest) *Message {
	payload := map[string]interface{}{
		"agent_id": req.AgentID,
	}

	if len(req.Tags) > 0 {
		payload["tags"] = req.Tags
	}

	return &Message{
		Type:      MsgTypeTaskRequest,
		AgentID:   req.AgentID,
		Timestamp: time.Now(),
		Payload:   payload,
	}
}

// CreateTaskResultMessage creates a task result message
func (p *Protocol) CreateTaskResultMessage(req *TaskResultRequest) *Message {
	payload := map[string]interface{}{
		"agent_id": req.AgentID,
		"task_id":  req.TaskID,
		"result":   req.Result,
	}

	return &Message{
		Type:      MsgTypeTaskResult,
		AgentID:   req.AgentID,
		Timestamp: time.Now(),
		Payload:   payload,
	}
}

// CreateTaskErrorMessage creates a task error message
func (p *Protocol) CreateTaskErrorMessage(req *TaskErrorRequest) *Message {
	payload := map[string]interface{}{
		"agent_id":      req.AgentID,
		"task_id":       req.TaskID,
		"error_message": req.ErrorMessage,
		"error_code":    req.ErrorCode,
		"retryable":     req.Retryable,
	}

	return &Message{
		Type:      MsgTypeTaskError,
		AgentID:   req.AgentID,
		Timestamp: time.Now(),
		Payload:   payload,
	}
}

// CreateAckMessage creates an acknowledgment message
func (p *Protocol) CreateAckMessage(status string, message string) *Message {
	return &Message{
		Type:      MsgTypeAck,
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"status":  status,
			"message": message,
		},
	}
}

// CreateTaskAssignedMessage creates a task assignment message
func (p *Protocol) CreateTaskAssignedMessage(task *Task) *Message {
	return &Message{
		Type:      MsgTypeTaskAssigned,
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"task": task,
		},
	}
}

// CreateNoTaskMessage creates a message indicating no tasks are available
func (p *Protocol) CreateNoTaskMessage() *Message {
	return &Message{
		Type:      MsgTypeNoTask,
		Timestamp: time.Now(),
		Payload: map[string]interface{}{
			"message": "No tasks available",
		},
	}
}

// CreateErrorMessage creates an error message
func (p *Protocol) CreateErrorMessage(errorMsg string) *Message {
	return &Message{
		Type:      MsgTypeError,
		Timestamp: time.Now(),
		Error:     errorMsg,
	}
}

// ParseMessage parses a JSON message into a Message struct
func (p *Protocol) ParseMessage(data []byte) (*Message, error) {
	var msg Message
	if err := json.Unmarshal(data, &msg); err != nil {
		return nil, err
	}
	return &msg, nil
}

// SerializeMessage serializes a Message struct to JSON
func (p *Protocol) SerializeMessage(msg *Message) ([]byte, error) {
	return json.Marshal(msg)
}

// ParseRegisterRequest parses a registration request from a message payload
func (p *Protocol) ParseRegisterRequest(payload map[string]interface{}) (*RegisterRequest, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	var req RegisterRequest
	if err := json.Unmarshal(data, &req); err != nil {
		return nil, err
	}

	return &req, nil
}

// ParseHeartbeatRequest parses a heartbeat request from a message payload
func (p *Protocol) ParseHeartbeatRequest(payload map[string]interface{}) (*HeartbeatRequest, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	var req HeartbeatRequest
	if err := json.Unmarshal(data, &req); err != nil {
		return nil, err
	}

	return &req, nil
}

// ParseTaskRequest parses a task request from a message payload
func (p *Protocol) ParseTaskRequest(payload map[string]interface{}) (*TaskRequest, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	var req TaskRequest
	if err := json.Unmarshal(data, &req); err != nil {
		return nil, err
	}

	return &req, nil
}

// ParseTaskResultRequest parses a task result request from a message payload
func (p *Protocol) ParseTaskResultRequest(payload map[string]interface{}) (*TaskResultRequest, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	var req TaskResultRequest
	if err := json.Unmarshal(data, &req); err != nil {
		return nil, err
	}

	return &req, nil
}

// ParseTaskErrorRequest parses a task error request from a message payload
func (p *Protocol) ParseTaskErrorRequest(payload map[string]interface{}) (*TaskErrorRequest, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	var req TaskErrorRequest
	if err := json.Unmarshal(data, &req); err != nil {
		return nil, err
	}

	return &req, nil
}

// ValidateMessage validates a message for required fields
func (p *Protocol) ValidateMessage(msg *Message) error {
	if msg.Type == "" {
		return ErrInvalidMessage("message type is required")
	}
	return validateMessageRequirements(msg)
}

type messageValidationRule struct {
	errorMessage string
	needsAgentID bool
	needsPayload bool
}

func messageValidationRules() map[MessageType]messageValidationRule {
	return map[MessageType]messageValidationRule{
		MsgTypeRegister: {
			errorMessage: "register message requires payload",
			needsPayload: true,
		},
		MsgTypeHeartbeat: {
			errorMessage: "heartbeat message requires agent_id",
			needsAgentID: true,
		},
		MsgTypeTaskRequest: {
			errorMessage: "task request requires agent_id",
			needsAgentID: true,
		},
		MsgTypeTaskResult: {
			errorMessage: "task result requires agent_id and payload",
			needsAgentID: true,
			needsPayload: true,
		},
		MsgTypeTaskError: {
			errorMessage: "task error requires agent_id and payload",
			needsAgentID: true,
			needsPayload: true,
		},
		MsgTypeUnregister: {
			errorMessage: "message requires agent_id",
			needsAgentID: true,
		},
		MsgTypeAck: {
			errorMessage: "message requires agent_id",
			needsAgentID: true,
		},
		MsgTypeNoTask: {
			errorMessage: "message requires agent_id",
			needsAgentID: true,
		},
		MsgTypeShutdown: {
			errorMessage: "message requires agent_id",
			needsAgentID: true,
		},
		MsgTypeTaskAssigned: {
			errorMessage: "task assigned requires agent_id and payload",
			needsAgentID: true,
			needsPayload: true,
		},
		MsgTypeError: {
			errorMessage: "error message requires payload",
			needsPayload: true,
		},
	}
}

func validateMessageRequirements(msg *Message) error {
	rule, ok := messageValidationRules()[msg.Type]
	if !ok {
		return nil
	}
	if rule.needsAgentID && msg.AgentID == "" {
		return ErrInvalidMessage(rule.errorMessage)
	}
	if rule.needsPayload && msg.Payload == nil {
		return ErrInvalidMessage(rule.errorMessage)
	}
	return nil
}

// ErrInvalidMessage creates an error for invalid messages
func ErrInvalidMessage(msg string) error {
	return &ProtocolError{Message: msg}
}

// ProtocolError represents a protocol-level error
type ProtocolError struct {
	Message string
}

func (e *ProtocolError) Error() string {
	return "protocol error: " + e.Message
}
