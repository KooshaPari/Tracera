package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// AIHandler handles AI service requests
type AIHandler struct {
	aiClient *clients.AIClient
}

// NewAIHandler creates a new AI handler
func NewAIHandler(aiClient *clients.AIClient) *AIHandler {
	return &AIHandler{
		aiClient: aiClient,
	}
}

// StreamChatRequest represents the HTTP request for streaming chat
type StreamChatRequest struct {
	Message   string                 `json:"message" validate:"required"`
	Context   map[string]interface{} `json:"context,omitempty"`
	ProjectID string                 `json:"project_id" validate:"required"`
	UserID    string                 `json:"user_id" validate:"required"`
}

// AnalyzeRequest represents the HTTP request for analysis
type AnalyzeRequest struct {
	Text      string `json:"text" validate:"required"`
	ProjectID string `json:"project_id" validate:"required"`
}

// StreamChat handles streaming AI chat requests
// @Summary Stream AI chat responses
// @Description Streams AI chat responses using Server-Sent Events (SSE)
// @Tags ai
// @Accept json
// @Produce text/event-stream
// @Param request body StreamChatRequest true "Stream chat request"
// @Success 200 {string} string "SSE stream of AI responses"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/ai/stream-chat [post]
func (h *AIHandler) StreamChat(c echo.Context) error {
	clientReq, err := h.parseStreamChatRequest(c)
	if err != nil {
		return err
	}

	eventChan, errChan := h.aiClient.StreamChat(c.Request().Context(), clientReq)
	h.setSSEHeaders(c)

	return h.streamChatEvents(c, eventChan, errChan)
}

func (h *AIHandler) parseStreamChatRequest(c echo.Context) (clients.StreamChatRequest, error) {
	var req StreamChatRequest
	if err := c.Bind(&req); err != nil {
		return clients.StreamChatRequest{}, echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return clients.StreamChatRequest{}, echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	return clients.StreamChatRequest{
		Message:   req.Message,
		Context:   req.Context,
		ProjectID: req.ProjectID,
		UserID:    req.UserID,
	}, nil
}

func (h *AIHandler) setSSEHeaders(c echo.Context) {
	c.Response().Header().Set("Content-Type", "text/event-stream")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("Connection", "keep-alive")
	c.Response().Header().Set("X-Accel-Buffering", "no") // Disable nginx buffering
	c.Response().WriteHeader(http.StatusOK)
}

func (h *AIHandler) streamChatEvents(
	echoCtx echo.Context,
	eventChan <-chan clients.SSEEvent,
	errChan <-chan error,
) error {
	loop := &streamChatLoop{
		handler:   h,
		ctx:       echoCtx,
		eventChan: eventChan,
		errChan:   errChan,
	}
	for {
		done, err := loop.step()
		if err != nil {
			return err
		}
		if done {
			return nil
		}
	}
}

type streamChatLoop struct {
	handler   *AIHandler
	ctx       echo.Context
	eventChan <-chan clients.SSEEvent
	errChan   <-chan error
}

func (loop *streamChatLoop) step() (bool, error) {
	select {
	case event, ok := <-loop.eventChan:
		return loop.handleEvent(event, ok)
	case err, ok := <-loop.errChan:
		return loop.handleError(err, ok)
	case <-loop.ctx.Request().Context().Done():
		return true, nil
	}
}

func (loop *streamChatLoop) handleEvent(event clients.SSEEvent, ok bool) (bool, error) {
	if !ok {
		return true, nil
	}

	if err := loop.handler.writeSSEEvent(loop.ctx, event); err != nil {
		return true, err
	}

	return false, nil
}

func (loop *streamChatLoop) handleError(err error, ok bool) (bool, error) {
	if !ok {
		loop.errChan = nil
		return false, nil
	}
	if err == nil {
		return false, nil
	}
	if writeErr := loop.handler.writeSSEError(loop.ctx, err); writeErr != nil {
		return true, writeErr
	}
	return true, err
}

func (h *AIHandler) writeSSEEvent(c echo.Context, event clients.SSEEvent) error {
	eventJSON, err := json.Marshal(event)
	if err != nil {
		return err
	}
	if _, err := fmt.Fprintf(c.Response(), "data: %s\n\n", string(eventJSON)); err != nil {
		return err
	}
	c.Response().Flush()
	return nil
}

func (h *AIHandler) writeSSEError(c echo.Context, streamErr error) error {
	errorEvent := clients.SSEEvent{
		Type:  "error",
		Error: streamErr.Error(),
	}
	errorJSON, err := json.Marshal(errorEvent)
	if err != nil {
		return err
	}
	if _, err := fmt.Fprintf(c.Response(), "data: %s\n\n", string(errorJSON)); err != nil {
		return err
	}
	c.Response().Flush()
	return nil
}

// Analyze handles non-streaming AI analysis requests
// @Summary Analyze text with AI
// @Description Performs AI analysis on provided text
// @Tags ai
// @Accept json
// @Produce json
// @Param request body AnalyzeRequest true "Analyze request"
// @Success 200 {object} clients.AnalysisResult "Analysis result"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/ai/analyze [post]
func (handler *AIHandler) Analyze(c echo.Context) error {
	var req AnalyzeRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	result, err := handler.aiClient.Analyze(c.Request().Context(), req.Text, req.ProjectID)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("Analysis failed: %v", err))
	}

	return c.JSON(http.StatusOK, result)
}

// RegisterAIRoutes registers AI handler routes
func RegisterAIRoutes(e *echo.Group, aiClient *clients.AIClient) {
	handler := NewAIHandler(aiClient)

	ai := e.Group("/ai")
	ai.POST("/stream-chat", handler.StreamChat)
	ai.POST("/analyze", handler.Analyze)
}
