package handlers

import (
	"errors"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/redis/go-redis/v9"
)

const (
	defaultSessionHours = 24
	defaultSessionTTL   = defaultSessionHours * time.Hour

	redisUserEmailKeyPrefix = "auth:user:email:"
)

// AuthHandler handles authentication endpoints
type AuthHandler struct {
	authProvider      auth.Provider
	redisClient       *redis.Client
	jwtSecret         string
	sessionTTL        time.Duration
	isProduction      bool
	passwordHasher    *auth.PasswordHasher
	passwordValidator *auth.PasswordStrengthValidator
}

// RegisterRequest represents a user registration request
type RegisterRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required,min=8"`
	Name     string `json:"name" validate:"required"`
}

// LoginRequest represents a login request
type LoginRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required,min=1"`
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

type storedUserRecord struct {
	ID           string                 `json:"id"`
	Email        string                 `json:"email"`
	Name         string                 `json:"name"`
	Role         string                 `json:"role"`
	ProjectID    string                 `json:"project_id"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
	PasswordHash string                 `json:"password_hash"`
	CreatedAt    time.Time              `json:"created_at"`
	UpdatedAt    time.Time              `json:"updated_at"`
}

var (
	errUserAlreadyExists = errors.New("user already exists")
	errUserNotFound      = errors.New("user not found")
)
