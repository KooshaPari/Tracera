package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

// createSessionToken creates a new session and returns a JWT token
func (h *AuthHandler) createSessionToken(ctx context.Context, user *auth.User) (string, error) {
	return h.upsertSessionToken(ctx, user, time.Now())
}

// validateSessionToken validates a JWT token and retrieves session data from Redis
func (handler *AuthHandler) validateSessionToken(ctx context.Context, tokenString string) (*auth.User, error) {
	if err := handler.ensureRedisConfigured(); err != nil {
		return nil, err
	}

	// Parse JWT token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if token.Method.Alg() != "HS256" {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(handler.jwtSecret), nil
	})
	if err != nil {
		return nil, fmt.Errorf("failed to parse token: %w", err)
	}

	if !token.Valid {
		return nil, errors.New("invalid token")
	}

	// Extract claims
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, errors.New("invalid token claims")
	}

	// Get user ID from token
	userID, ok := claims["sub"].(string)
	if !ok || userID == "" {
		return nil, errors.New("missing user ID in token")
	}

	// Retrieve session from Redis
	sessionKey := "session:" + userID
	sessionJSON, err := handler.redisClient.Get(ctx, sessionKey).Result()
	if err == redis.Nil {
		return nil, errors.New("session not found or expired")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve session: %w", err)
	}

	// Deserialize session data
	var sessionData SessionData
	if err := json.Unmarshal([]byte(sessionJSON), &sessionData); err != nil {
		return nil, fmt.Errorf("failed to deserialize session data: %w", err)
	}

	// Convert to User object
	user := &auth.User{
		ID:        sessionData.UserID,
		Email:     sessionData.Email,
		Name:      sessionData.Name,
		ProjectID: sessionData.ProjectID,
		Role:      sessionData.Role,
		Metadata:  sessionData.Metadata,
	}

	return user, nil
}

// extendSession extends the session TTL and generates a new token
func (h *AuthHandler) extendSession(ctx context.Context, user *auth.User) (string, error) {
	return h.upsertSessionToken(ctx, user, time.Now())
}

func (h *AuthHandler) upsertSessionToken(ctx context.Context, user *auth.User, now time.Time) (string, error) {
	if err := h.ensureRedisConfigured(); err != nil {
		return "", err
	}

	sessionKey := "session:" + user.ID
	sessionData := SessionData{
		UserID:     user.ID,
		Email:      user.Email,
		Name:       user.Name,
		ProjectID:  user.ProjectID,
		Role:       user.Role,
		CreatedAt:  now,
		LastActive: now,
		Metadata:   user.Metadata,
	}

	sessionJSON, err := json.Marshal(sessionData)
	if err != nil {
		return "", fmt.Errorf("failed to serialize session data: %w", err)
	}

	if err := h.redisClient.Set(ctx, sessionKey, sessionJSON, h.sessionTTL).Err(); err != nil {
		return "", fmt.Errorf("failed to store session: %w", err)
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"sub":        user.ID,
		"email":      user.Email,
		"name":       user.Name,
		"project_id": user.ProjectID,
		"role":       user.Role,
		"exp":        now.Add(h.sessionTTL).Unix(),
		"iat":        now.Unix(),
	})

	tokenString, err := token.SignedString([]byte(h.jwtSecret))
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return tokenString, nil
}

// setAuthCookie sets the authentication cookie with HttpOnly flag
func (h *AuthHandler) setAuthCookie(c echo.Context, token string) {
	cookie := &http.Cookie{
		Name:     "auth_token",
		Value:    token,
		Path:     "/",
		MaxAge:   int(h.sessionTTL.Seconds()),
		HttpOnly: true,
		Secure:   h.isProduction, // Only send over HTTPS in production
		SameSite: http.SameSiteStrictMode,
	}
	c.SetCookie(cookie)
}

// clearAuthCookie clears the authentication cookie
func (h *AuthHandler) clearAuthCookie(c echo.Context) {
	cookie := &http.Cookie{
		Name:     "auth_token",
		Value:    "",
		Path:     "/",
		MaxAge:   -1, // Expire immediately
		HttpOnly: true,
		Secure:   h.isProduction,
		SameSite: http.SameSiteStrictMode,
	}
	c.SetCookie(cookie)
}
