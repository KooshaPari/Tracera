// Package infrastructure wires infrastructure dependencies.
package infrastructure

import (
	"fmt"
	"time"

	"gorm.io/gorm"
)

type notificationSchema struct {
	ID        string     `gorm:"primaryKey;type:varchar(36)"`
	UserID    string     `gorm:"type:varchar(255);not null;index"`
	Type      string     `gorm:"type:varchar(50);not null;default:info"`
	Title     string     `gorm:"type:varchar(255);not null"`
	Message   string     `gorm:"type:text;not null"`
	Link      *string    `gorm:"type:varchar(500)"`
	ReadAt    *time.Time `gorm:"type:timestamptz"`
	CreatedAt time.Time  `gorm:"type:timestamptz;not null;default:now();index"`
	UpdatedAt time.Time  `gorm:"type:timestamptz;not null;default:now()"`
	ExpiresAt *time.Time `gorm:"type:timestamptz;index"`
}

func (notificationSchema) TableName() string {
	return "notifications"
}

func migrateNotificationsSchema(gormDB *gorm.DB) error {
	if !gormDB.Migrator().HasTable(&notificationSchema{}) {
		if err := gormDB.AutoMigrate(&notificationSchema{}); err != nil {
			return fmt.Errorf("failed to create notifications schema: %w", err)
		}
		return nil
	}

	if !gormDB.Migrator().HasColumn(&notificationSchema{}, "expires_at") {
		if err := gormDB.Exec(
			"ALTER TABLE notifications ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ",
		).Error; err != nil {
			return fmt.Errorf("failed to add notifications.expires_at: %w", err)
		}
	}
	if err := gormDB.Exec(
		"CREATE INDEX IF NOT EXISTS idx_notifications_expires_at ON notifications(expires_at)",
	).Error; err != nil {
		return fmt.Errorf("failed to index notifications.expires_at: %w", err)
	}
	return nil
}
