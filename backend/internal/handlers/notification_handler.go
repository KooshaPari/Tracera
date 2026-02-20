package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

const (
	notificationPingInterval = 30 * time.Second
	boolTrue                 = "true"
	notificationDefaultLimit = 50
)

// NotificationHandler handles notification-related HTTP requests
type NotificationHandler struct {
	service      *services.NotificationService
	authProvider auth.Provider
}

// NewNotificationHandler creates a new notification handler
func NewNotificationHandler(service *services.NotificationService, authProvider auth.Provider) *NotificationHandler {
	return &NotificationHandler{
		service:      service,
		authProvider: authProvider,
	}
}

// CreateNotificationRequest represents a request to create a notification
type CreateNotificationRequest struct {
	UserID  string                    `json:"user_id" validate:"required"`
	Type    services.NotificationType `json:"type" validate:"required,oneof=info success warning error"`
	Title   string                    `json:"title" validate:"required,max=200"`
	Message string                    `json:"message" validate:"required,max=1000"`
	Link    *string                   `json:"link,omitempty"`
}

// NotificationResponse represents a notification response
type NotificationResponse struct {
	ID        string                    `json:"id"`
	UserID    string                    `json:"user_id"`
	Type      services.NotificationType `json:"type"`
	Title     string                    `json:"title"`
	Message   string                    `json:"message"`
	Link      *string                   `json:"link,omitempty"`
	ReadAt    *time.Time                `json:"read_at,omitempty"`
	CreatedAt time.Time                 `json:"created_at"`
}

// ListNotifications godoc
// @Summary List notifications
// @Description Get notifications for the authenticated user
// @Tags notifications
// @Accept json
// @Produce json
// @Param unread_only query bool false "Only unread notifications"
// @Param limit query int false "Maximum number of notifications to return" default(50)
// @Success 200 {array} NotificationResponse
// @Failure 401 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /notifications [get]
// @Security ApiKeyAuth
func (h *NotificationHandler) ListNotifications(c echo.Context) error {
	// Get user from context (set by auth middleware)
	userID := c.Get("user_id")
	if userID == nil {
		return echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}
	userIDStr, ok := userID.(string)
	if !ok || userIDStr == "" {
		return echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}

	unreadOnly := c.QueryParam("unread_only") == boolTrue
	limit := notificationDefaultLimit // Default limit
	if l := c.QueryParam("limit"); l != "" {
		if _, err := fmt.Sscanf(l, "%d", &limit); err != nil {
			limit = notificationDefaultLimit
		}
	}

	notifications, err := h.service.List(c.Request().Context(), userIDStr, unreadOnly, limit)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to list notifications: %v", err))
	}

	responses := make([]NotificationResponse, len(notifications))
	for i, notification := range notifications {
		responses[i] = NotificationResponse{
			ID:        notification.ID,
			UserID:    notification.UserID,
			Type:      notification.Type,
			Title:     notification.Title,
			Message:   notification.Message,
			Link:      notification.Link,
			ReadAt:    notification.ReadAt,
			CreatedAt: notification.CreatedAt,
		}
	}

	return c.JSON(http.StatusOK, responses)
}

func getNotificationUserID(c echo.Context) (string, error) {
	userID := c.Get("user_id")
	if userID == nil {
		return "", echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}
	userIDStr, ok := userID.(string)
	if !ok || userIDStr == "" {
		return "", echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}
	return userIDStr, nil
}

func getNotificationID(c echo.Context) (string, error) {
	notificationID := c.Param("id")
	if notificationID == "" {
		return "", echo.NewHTTPError(http.StatusBadRequest, "notification ID is required")
	}
	return notificationID, nil
}

// MarkAsRead godoc
// @Summary Mark notification as read
// @Description Mark a specific notification as read
// @Tags notifications
// @Accept json
// @Produce json
// @Param id path string true "Notification ID"
// @Success 200 {object} map[string]string
// @Failure 401 {object} ErrorResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /notifications/{id}/read [post]
// @Security ApiKeyAuth
func (h *NotificationHandler) MarkAsRead(c echo.Context) error {
	userIDStr, err := getNotificationUserID(c)
	if err != nil {
		return err
	}

	notificationID, err := getNotificationID(c)
	if err != nil {
		return err
	}

	if err := h.service.MarkAsRead(c.Request().Context(), userIDStr, notificationID); err != nil {
		if err.Error() == "notification not found" {
			return echo.NewHTTPError(http.StatusNotFound, "notification not found")
		}
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to mark as read: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

// MarkAllAsRead godoc
// @Summary Mark all notifications as read
// @Description Mark all notifications for the authenticated user as read
// @Tags notifications
// @Accept json
// @Produce json
// @Success 200 {object} map[string]string
// @Failure 401 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /notifications/read-all [post]
// @Security ApiKeyAuth
func (h *NotificationHandler) MarkAllAsRead(c echo.Context) error {
	userID := c.Get("user_id")
	if userID == nil {
		return echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}
	userIDStr, ok := userID.(string)
	if !ok || userIDStr == "" {
		return echo.NewHTTPError(http.StatusUnauthorized, "user not authenticated")
	}

	if err := h.service.MarkAllAsRead(c.Request().Context(), userIDStr); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to mark all as read: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

// DeleteNotification godoc
// @Summary Delete notification
// @Description Delete a specific notification
// @Tags notifications
// @Accept json
// @Produce json
// @Param id path string true "Notification ID"
// @Success 200 {object} map[string]string
// @Failure 401 {object} ErrorResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /notifications/{id} [delete]
// @Security ApiKeyAuth
func (h *NotificationHandler) DeleteNotification(c echo.Context) error {
	userIDStr, err := getNotificationUserID(c)
	if err != nil {
		return err
	}

	notificationID, err := getNotificationID(c)
	if err != nil {
		return err
	}

	if err := h.service.Delete(c.Request().Context(), userIDStr, notificationID); err != nil {
		if err.Error() == "notification not found" {
			return echo.NewHTTPError(http.StatusNotFound, "notification not found")
		}
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to delete: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

// StreamNotifications godoc
// @Summary Stream notifications via Server-Sent Events
// @Description Establishes an SSE connection for real-time notifications
// @Tags notifications
// @Produce text/event-stream
// @Success 200 {string} string "SSE stream"
// @Failure 401 {object} ErrorResponse
// @Router /notifications/stream [get]
// @Security ApiKeyAuth
func (h *NotificationHandler) StreamNotifications(c echo.Context) error {
	return h.streamNotifications(c)
}

func (h *NotificationHandler) streamNotifications(c echo.Context) error {
	// Get user from context (set by auth middleware)
	userIDStr, err := getNotificationUserID(c)
	if err != nil {
		return err
	}

	setupSSEHeaders(c)

	// Subscribe to notifications
	subscriberID, eventChan := h.service.Subscribe(userIDStr)
	defer h.service.Unsubscribe(userIDStr, subscriberID)

	// Create context with cancellation
	ctx, cancel := context.WithCancel(c.Request().Context())
	defer cancel()

	// Send initial connection event
	if err := sendSSEConnected(c.Response()); err != nil {
		return err
	}
	c.Response().Flush()

	// Create ticker for keep-alive ping messages
	pingTicker := time.NewTicker(notificationPingInterval)
	defer pingTicker.Stop()

	return h.runNotificationStream(ctx, c, userIDStr, eventChan, pingTicker)
}

func setupSSEHeaders(c echo.Context) {
	c.Response().Header().Set("Content-Type", "text/event-stream")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("Connection", "keep-alive")
	c.Response().Header().Set("X-Accel-Buffering", "no")
}

func sendSSEConnected(w http.ResponseWriter) error {
	return writeSSEEvent(w, "connected", map[string]string{
		"status":    "connected",
		"timestamp": strconv.FormatInt(time.Now().Unix(), 10),
	})
}

func (h *NotificationHandler) runNotificationStream(
	ctx context.Context,
	c echo.Context,
	userIDStr string,
	eventChan <-chan *services.NotificationEvent,
	pingTicker *time.Ticker,
) error {
	for {
		select {
		case <-ctx.Done():
			slog.Info("SSE client disconnected (user )", "user", userIDStr)
			return nil
		case event, ok := <-eventChan:
			if !ok {
				return nil
			}
			if err := h.writeSSENotificationEvent(c, event); err != nil {
				return err
			}
		case <-pingTicker.C:
			if err := h.writeSSEPing(c); err != nil {
				return err
			}
		}
	}
}

func (h *NotificationHandler) writeSSENotificationEvent(
	c echo.Context,
	event *services.NotificationEvent,
) error {
	if err := writeSSEEvent(c.Response(), event.Type, event); err != nil {
		slog.Error("Error writing SSE event", "error", err)
		return err
	}
	c.Response().Flush()
	return nil
}

func (h *NotificationHandler) writeSSEPing(c echo.Context) error {
	if err := writeSSEEvent(c.Response(), "ping", map[string]interface{}{
		"timestamp": time.Now().Unix(),
	}); err != nil {
		slog.Error("Error sending keep-alive ping", "error", err)
		return err
	}
	c.Response().Flush()
	return nil
}

// writeSSEEvent writes an SSE event to the response
func writeSSEEvent(w http.ResponseWriter, eventType string, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal event data: %w", err)
	}

	// Write event type
	if _, err := fmt.Fprintf(w, "event: %s\n", eventType); err != nil {
		return err
	}

	// Write data
	if _, err := fmt.Fprintf(w, "data: %s\n\n", jsonData); err != nil {
		return err
	}

	return nil
}

// CreateNotification godoc
// @Summary Create notification (admin/system only)
// @Description Create a new notification for a user
// @Tags notifications
// @Accept json
// @Produce json
// @Param notification body CreateNotificationRequest true "Notification details"
// @Success 201 {object} NotificationResponse
// @Failure 400 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /notifications [post]
// @Security ApiKeyAuth
func (h *NotificationHandler) CreateNotification(c echo.Context) error {
	var req CreateNotificationRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, fmt.Sprintf("invalid request: %v", err))
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, fmt.Sprintf("validation failed: %v", err))
	}

	notification, err := h.service.Create(c.Request().Context(), req.UserID, req.Type, req.Title, req.Message, req.Link)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to create notification: %v", err))
	}

	response := NotificationResponse{
		ID:        notification.ID,
		UserID:    notification.UserID,
		Type:      notification.Type,
		Title:     notification.Title,
		Message:   notification.Message,
		Link:      notification.Link,
		ReadAt:    notification.ReadAt,
		CreatedAt: notification.CreatedAt,
	}

	return c.JSON(http.StatusCreated, response)
}
