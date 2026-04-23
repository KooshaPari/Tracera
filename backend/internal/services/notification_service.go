package services

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// NotificationType defines the type of notification
type NotificationType string

const (
	// NotificationTypeInfo is an informational notification.
	NotificationTypeInfo NotificationType = "info"
	// NotificationTypeSuccess indicates a successful action or outcome.
	NotificationTypeSuccess NotificationType = "success"
	// NotificationTypeWarning indicates a warning that may require attention.
	NotificationTypeWarning NotificationType = "warning"
	// NotificationTypeError indicates an error notification.
	NotificationTypeError NotificationType = "error"
)

const (
	notificationBufferSize = 100
)

// Notification represents a user notification
type Notification struct {
	ID        string           `json:"id" gorm:"primaryKey"`
	UserID    string           `json:"user_id" gorm:"index"`
	Type      NotificationType `json:"type"`
	Title     string           `json:"title"`
	Message   string           `json:"message"`
	Link      *string          `json:"link,omitempty"`
	ReadAt    *time.Time       `json:"read_at,omitempty"`
	CreatedAt time.Time        `json:"created_at" gorm:"index"`
	ExpiresAt *time.Time       `json:"expires_at,omitempty" gorm:"index"`
}

// NotificationEvent represents a notification event for broadcasting
type NotificationEvent struct {
	Type         string       `json:"type"` // "notification", "read", "delete"
	Notification Notification `json:"notification,omitempty"`
	UserID       string       `json:"user_id"`
	Timestamp    int64        `json:"timestamp"`
}

type notificationEventBus interface {
	PublishNotification(ctx context.Context, userID string, event *NotificationEvent) error
	SubscribeNotifications(ctx context.Context, handler func(*NotificationEvent)) (func() error, error)
}

// NotificationService handles notification creation and broadcasting
type NotificationService struct {
	db          *gorm.DB
	eventBus    notificationEventBus
	pubSubMu    sync.RWMutex
	subscribers map[string]map[string]chan *NotificationEvent // userID -> subscriberID -> channel
	unsubscribe func() error
}

// NewNotificationService creates a new notification service
func NewNotificationService(db *gorm.DB, eventBus notificationEventBus) *NotificationService {
	ns := &NotificationService{
		db:          db,
		eventBus:    eventBus,
		subscribers: make(map[string]map[string]chan *NotificationEvent),
	}

	ns.startEventBusListener(context.Background())

	return ns
}

// TableName specifies the database table name
func (Notification) TableName() string {
	return "notifications"
}

// Create creates a new notification and broadcasts it
func (ns *NotificationService) Create(
	ctx context.Context, userID string, notifType NotificationType, title, message string, link *string,
) (*Notification, error) {
	notification := &Notification{
		ID:        uuid.New().String(),
		UserID:    userID,
		Type:      notifType,
		Title:     title,
		Message:   message,
		Link:      link,
		CreatedAt: time.Now(),
	}

	// Save to database
	if err := ns.db.WithContext(ctx).Create(notification).Error; err != nil {
		return nil, fmt.Errorf("failed to create notification: %w", err)
	}

	// Broadcast through NATS so every backend instance can fan out to local SSE subscribers.
	if err := ns.broadcastNotification(ctx, notification); err != nil {
		slog.Error("Warning: Failed to broadcast notification", "error", err)
	}

	return notification, nil
}

// List retrieves notifications for a user
func (ns *NotificationService) List(ctx context.Context, userID string, unreadOnly bool, limit int) ([]*Notification, error) {
	var notifications []*Notification
	query := ns.db.WithContext(ctx).Where("user_id = ?", userID)

	if unreadOnly {
		query = query.Where("read_at IS NULL")
	}

	// Filter out expired notifications
	query = query.Where("expires_at IS NULL OR expires_at > ?", time.Now())

	if limit > 0 {
		query = query.Limit(limit)
	}

	if err := query.Order("created_at DESC").Find(&notifications).Error; err != nil {
		return nil, fmt.Errorf("failed to list notifications: %w", err)
	}

	return notifications, nil
}

// MarkAsRead marks a notification as read
func (ns *NotificationService) MarkAsRead(ctx context.Context, userID, notificationID string) error {
	now := time.Now()
	result := ns.db.WithContext(ctx).
		Model(&Notification{}).
		Where("id = ? AND user_id = ?", notificationID, userID).
		Update("read_at", now)

	if result.Error != nil {
		return fmt.Errorf("failed to mark notification as read: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return errors.New("notification not found")
	}

	// Broadcast read event
	event := &NotificationEvent{
		Type:      "read",
		UserID:    userID,
		Timestamp: time.Now().Unix(),
		Notification: Notification{
			ID:     notificationID,
			ReadAt: &now,
		},
	}
	if err := ns.broadcastEvent(ctx, userID, event); err != nil {
		slog.Warn("failed to broadcast notification event", "user_id", userID, "error", err)
	}

	return nil
}

// MarkAllAsRead marks all notifications for a user as read
func (ns *NotificationService) MarkAllAsRead(ctx context.Context, userID string) error {
	now := time.Now()
	result := ns.db.WithContext(ctx).
		Model(&Notification{}).
		Where("user_id = ? AND read_at IS NULL", userID).
		Update("read_at", now)

	if result.Error != nil {
		return fmt.Errorf("failed to mark all notifications as read: %w", result.Error)
	}

	// Broadcast read-all event
	event := &NotificationEvent{
		Type:      "read_all",
		UserID:    userID,
		Timestamp: time.Now().Unix(),
	}
	if err := ns.broadcastEvent(ctx, userID, event); err != nil {
		slog.Warn("failed to broadcast notification event", "user_id", userID, "error", err)
	}

	return nil
}

// Delete deletes a notification
func (ns *NotificationService) Delete(ctx context.Context, userID, notificationID string) error {
	result := ns.db.WithContext(ctx).
		Where("id = ? AND user_id = ?", notificationID, userID).
		Delete(&Notification{})

	if result.Error != nil {
		return fmt.Errorf("failed to delete notification: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return errors.New("notification not found")
	}

	// Broadcast delete event
	event := &NotificationEvent{
		Type:      "delete",
		UserID:    userID,
		Timestamp: time.Now().Unix(),
		Notification: Notification{
			ID: notificationID,
		},
	}
	if err := ns.broadcastEvent(ctx, userID, event); err != nil {
		slog.Warn("failed to broadcast notification event", "user_id", userID, "error", err)
	}

	return nil
}

// Subscribe creates a subscription for a user's notifications
func (ns *NotificationService) Subscribe(userID string) (string, <-chan *NotificationEvent) {
	subscriberID := uuid.New().String()
	ch := make(chan *NotificationEvent, notificationBufferSize) // Buffer to prevent blocking

	ns.pubSubMu.Lock()
	if ns.subscribers[userID] == nil {
		ns.subscribers[userID] = make(map[string]chan *NotificationEvent)
	}
	ns.subscribers[userID][subscriberID] = ch
	ns.pubSubMu.Unlock()

	slog.Info("User subscribed to notifications (subscriber )", "user", userID, "id", subscriberID)

	return subscriberID, ch
}

// Unsubscribe removes a subscription
func (ns *NotificationService) Unsubscribe(userID, subscriberID string) {
	ns.pubSubMu.Lock()
	defer ns.pubSubMu.Unlock()

	if subs, ok := ns.subscribers[userID]; ok {
		if ch, exists := subs[subscriberID]; exists {
			close(ch)
			delete(subs, subscriberID)
			slog.Info("User unsubscribed from notifications (subscriber )", "user", userID, "id", subscriberID)
		}
		if len(subs) == 0 {
			delete(ns.subscribers, userID)
		}
	}
}

// broadcastNotification broadcasts a notification through the configured event bus
func (ns *NotificationService) broadcastNotification(ctx context.Context, notification *Notification) error {
	event := &NotificationEvent{
		Type:         "notification",
		Notification: *notification,
		UserID:       notification.UserID,
		Timestamp:    time.Now().Unix(),
	}

	return ns.broadcastEvent(ctx, notification.UserID, event)
}

// broadcastEvent broadcasts an event through NATS and to local subscribers
func (ns *NotificationService) broadcastEvent(ctx context.Context, userID string, event *NotificationEvent) error {
	if ns.eventBus == nil {
		ns.broadcastToLocalSubscribers(userID, event)
		return nil
	}

	if err := ns.eventBus.PublishNotification(ctx, userID, event); err != nil {
		return fmt.Errorf("failed to publish notification event: %w", err)
	}

	return nil
}

// startEventBusListener starts listening for notification events from NATS.
func (ns *NotificationService) startEventBusListener(ctx context.Context) {
	if ns.eventBus == nil {
		slog.Warn("NATS notification bus not configured, using local-only notifications")
		return
	}

	unsubscribe, err := ns.eventBus.SubscribeNotifications(ctx, func(event *NotificationEvent) {
		ns.broadcastToLocalSubscribers(event.UserID, event)
	})
	if err != nil {
		slog.Error("failed to subscribe to NATS notification events", "error", err)
		return
	}

	ns.unsubscribe = unsubscribe
	slog.Info("Notification service: NATS notification listener started")
}

// broadcastToLocalSubscribers broadcasts to local SSE subscribers
func (ns *NotificationService) broadcastToLocalSubscribers(userID string, event *NotificationEvent) {
	ns.pubSubMu.RLock()
	subscribers, ok := ns.subscribers[userID]
	ns.pubSubMu.RUnlock()

	if !ok {
		return
	}

	// Send to all subscribers for this user
	for subscriberID, ch := range subscribers {
		select {
		case ch <- event:
			// Event sent successfully
		default:
			slog.Warn("Warning: Subscriber channel full, skipping event", "id", subscriberID)
		}
	}
}

// CleanupExpired removes expired notifications
func (ns *NotificationService) CleanupExpired(ctx context.Context) error {
	result := ns.db.WithContext(ctx).
		Where("expires_at IS NOT NULL AND expires_at < ?", time.Now()).
		Delete(&Notification{})

	if result.Error != nil {
		return fmt.Errorf("failed to cleanup expired notifications: %w", result.Error)
	}

	if result.RowsAffected > 0 {
		slog.Info("Cleaned up expired notifications", "value", result.RowsAffected)
	}

	return nil
}

// Close releases notification event-bus subscriptions.
func (ns *NotificationService) Close() error {
	if ns.unsubscribe == nil {
		return nil
	}
	if err := ns.unsubscribe(); err != nil {
		return fmt.Errorf("failed to unsubscribe from notification events: %w", err)
	}
	ns.unsubscribe = nil
	return nil
}
