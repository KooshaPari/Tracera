package handlers

import (
	"time"

	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// NewAuthHandler creates a new authentication handler
func NewAuthHandler(
	authProvider auth.Provider,
	redisClient *redis.Client,
	jwtSecret string,
	sessionTTL time.Duration,
	isProduction bool,
) *AuthHandler {
	if sessionTTL == 0 {
		sessionTTL = defaultSessionTTL // Default 24 hours
	}

	return &AuthHandler{
		authProvider: authProvider,
		redisClient:  redisClient,
		jwtSecret:    jwtSecret,
		sessionTTL:   sessionTTL,
		isProduction: isProduction,
	}
}
