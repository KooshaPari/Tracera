package handlers

import (
	"time"

	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

const (
	defaultSessionHours = 24
	defaultSessionTTL   = defaultSessionHours * time.Hour
)

// AuthHandler handles authentication endpoints
type AuthHandler struct {
	authProvider auth.Provider
	redisClient  *redis.Client
	jwtSecret    string
	sessionTTL   time.Duration
	isProduction bool
}

// AuthResponse represents an authentication response
type AuthResponse struct {
	User        *auth.User `json:"user"`
	Token       string     `json:"token,omitempty"`
	AccessToken string     `json:"access_token,omitempty"`
	ExpiresIn   int64      `json:"expires_in,omitempty"`
}

// SessionData represents session data stored in Redis
type SessionData struct {
	UserID     string                 `json:"user_id"`
	Email      string                 `json:"email"`
	Name       string                 `json:"name"`
	ProjectID  string                 `json:"project_id"`
	Role       string                 `json:"role"`
	CreatedAt  time.Time              `json:"created_at"`
	LastActive time.Time              `json:"last_active"`
	Metadata   map[string]interface{} `json:"metadata"`
}
