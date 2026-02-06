package agents

import (
	"fmt"
)

const (
	// coordinatorSingletonLockKey is a stable Postgres advisory lock key.
	// Coordinator mode is not safe for multi-instance operation without atomic claims, so we enforce a singleton.
	coordinatorSingletonLockKey int64 = 42424242
)

type advisoryLockRow struct {
	Locked bool `gorm:"column:locked"`
}

func (c *Coordinator) acquireSingletonLock() error {
	if c.db == nil {
		return nil
	}

	// Only enforce singleton when running on Postgres.
	if c.db.Dialector == nil || c.db.Dialector.Name() != "postgres" {
		return nil
	}

	var row advisoryLockRow
	if err := c.db.Raw("SELECT pg_try_advisory_lock(?) AS locked", coordinatorSingletonLockKey).Scan(&row).Error; err != nil {
		return fmt.Errorf("failed to acquire coordinator singleton lock: %w", err)
	}
	if !row.Locked {
		return fmt.Errorf("coordinator singleton lock is already held (another instance is running)")
	}
	return nil
}

func (c *Coordinator) releaseSingletonLock() error {
	if c.db == nil {
		return nil
	}
	if c.db.Dialector == nil || c.db.Dialector.Name() != "postgres" {
		return nil
	}
	if err := c.db.Exec("SELECT pg_advisory_unlock(?)", coordinatorSingletonLockKey).Error; err != nil {
		return fmt.Errorf("failed to release coordinator singleton lock: %w", err)
	}
	return nil
}
