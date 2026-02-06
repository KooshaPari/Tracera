package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
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
	notificationRetryDelay = 1 * time.Second
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

// NotificationService handles notification creation and broadcasting
type NotificationService struct {
	db          *gorm.DB
	redis       *redis.Client
	pubSubMu    sync.RWMutex
	subscribers map[string]map[string]chan *NotificationEvent // userID -> subscriberID -> channel
}

// NewNotificationService creates a new notification service
func NewNotificationService(db *gorm.DB, redisClient *redis.Client) *NotificationService {
	ns := &NotificationService{
		db:          db,
		redis:       redisClient,
		subscribers: make(map[string]map[string]chan *NotificationEvent),
	}

	// Start Redis pub/sub listener
	go ns.startRedisPubSubListener()

	return ns
}

// TableName specifies the database table name
func (Notification) TableName() string {
	return "notifications"
}

// Create creates a new notification and broadcasts it
func (ns *NotificationService) Create(ctx context.Context, userID string, notifType NotificationType, title, message string, link *string) (*Notification, error) {
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

	// Broadcast via Redis pub/sub
	if err := ns.broadcastNotification(ctx, notification); err != nil {
		log.Printf("Warning: Failed to broadcast notification: %v", err)
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
	_ = ns.broadcastEvent(ctx, userID, event)

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
	_ = ns.broadcastEvent(ctx, userID, event)

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
	_ = ns.broadcastEvent(ctx, userID, event)

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

	log.Printf("User %s subscribed to notifications (subscriber: %s)", userID, subscriberID)

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
			log.Printf("User %s unsubscribed from notifications (subscriber: %s)", userID, subscriberID)
		}
		if len(subs) == 0 {
			delete(ns.subscribers, userID)
		}
	}
}

// broadcastNotification broadcasts a notification via Redis pub/sub
func (ns *NotificationService) broadcastNotification(ctx context.Context, notification *Notification) error {
	event := &NotificationEvent{
		Type:         "notification",
		Notification: *notification,
		UserID:       notification.UserID,
		Timestamp:    time.Now().Unix(),
	}

	return ns.broadcastEvent(ctx, notification.UserID, event)
}

// broadcastEvent broadcasts an event via Redis pub/sub
func (ns *NotificationService) broadcastEvent(ctx context.Context, userID string, event *NotificationEvent) error {
	if ns.redis == nil {
		// Fallback to local broadcasting only
		ns.broadcastToLocalSubscribers(userID, event)
		return nil
	}

	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal notification event: %w", err)
	}

	channel := "notifications:" + userID
	if err := ns.redis.Publish(ctx, channel, data).Err(); err != nil {
		return fmt.Errorf("failed to publish to Redis: %w", err)
	}

	return nil
}

// startRedisPubSubListener starts listening to Redis pub/sub for notifications
func (ns *NotificationService) startRedisPubSubListener() {
	if ns.redis == nil {
		log.Println("Redis not configured, skipping pub/sub listener")
		return
	}

	ctx := context.Background()

	// Subscribe to notification pattern (all user channels)
	pubsub := ns.redis.PSubscribe(ctx, "notifications:*")
	defer func() { _ = pubsub.Close() }()

	log.Println("Notification service: Redis pub/sub listener started")

	for {
		msg, err := pubsub.ReceiveMessage(ctx)
		if err != nil {
			log.Printf("Error receiving Redis message: %v", err)
			time.Sleep(notificationRetryDelay)
			continue
		}

		var event NotificationEvent
		if err := json.Unmarshal([]byte(msg.Payload), &event); err != nil {
			log.Printf("Error unmarshaling notification event: %v", err)
			continue
		}

		// Broadcast to local subscribers
		ns.broadcastToLocalSubscribers(event.UserID, &event)
	}
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
			log.Printf("Warning: Subscriber %s channel full, skipping event", subscriberID)
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
		log.Printf("Cleaned up %d expired notifications", result.RowsAffected)
	}

	return nil
}
