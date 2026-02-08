package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/redis/go-redis/v9"
)

func (h *AuthHandler) ensureRedisConfigured() error {
	if h.redisClient == nil {
		return errors.New("redis client not configured")
	}
	return nil
}

func normalizeEmail(email string) string {
	return strings.ToLower(strings.TrimSpace(email))
}

func (h *AuthHandler) userExists(ctx context.Context, email string) (bool, error) {
	if err := h.ensureRedisConfigured(); err != nil {
		return false, err
	}
	if email == "" {
		return false, errors.New("email is required")
	}
	_, err := h.redisClient.Get(ctx, h.userEmailKey(email)).Result()
	if err == redis.Nil {
		return false, nil
	}
	if err != nil {
		return false, fmt.Errorf("failed to check user: %w", err)
	}
	return true, nil
}

func (h *AuthHandler) storeUserRecord(ctx context.Context, user *auth.User, passwordHash string) error {
	if err := h.ensureRedisConfigured(); err != nil {
		return err
	}
	if user == nil {
		return errors.New("user is required")
	}
	if user.Email == "" {
		return errors.New("user email is required")
	}
	if passwordHash == "" {
		return errors.New("password hash is required")
	}

	normalizedEmail := normalizeEmail(user.Email)
	if user.Metadata == nil {
		user.Metadata = make(map[string]interface{})
	}

	now := time.Now()
	record := storedUserRecord{
		ID:           user.ID,
		Email:        normalizedEmail,
		Name:         user.Name,
		Role:         user.Role,
		ProjectID:    user.ProjectID,
		Metadata:     user.Metadata,
		PasswordHash: passwordHash,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	payload, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to serialize user record: %w", err)
	}

	created, err := h.redisClient.SetNX(ctx, h.userEmailKey(normalizedEmail), payload, 0).Result()
	if err != nil {
		return fmt.Errorf("failed to store user record: %w", err)
	}
	if !created {
		return errUserAlreadyExists
	}
	return nil
}

func (h *AuthHandler) getUserRecordByEmail(ctx context.Context, email string) (*storedUserRecord, error) {
	if err := h.ensureRedisConfigured(); err != nil {
		return nil, err
	}
	if email == "" {
		return nil, errors.New("email is required")
	}

	result, err := h.redisClient.Get(ctx, h.userEmailKey(email)).Result()
	if err == redis.Nil {
		return nil, errUserNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to fetch user record: %w", err)
	}

	var record storedUserRecord
	if err := json.Unmarshal([]byte(result), &record); err != nil {
		return nil, fmt.Errorf("failed to decode user record: %w", err)
	}
	return &record, nil
}

func (h *AuthHandler) userEmailKey(email string) string {
	return redisUserEmailKeyPrefix + normalizeEmail(email)
}

func (r *storedUserRecord) toUser() *auth.User {
	if r == nil {
		return nil
	}
	metadata := r.Metadata
	if metadata == nil {
		metadata = make(map[string]interface{})
	}

	return &auth.User{
		ID:        r.ID,
		Email:     r.Email,
		Name:      r.Name,
		Role:      r.Role,
		ProjectID: r.ProjectID,
		Metadata:  metadata,
	}
}
