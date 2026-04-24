package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

func (h *AuthHandler) ensureRedisConfigured() error {
	if h.redisClient == nil {
		return errors.New("redis client not configured")
	}
	return nil
}

// createSessionToken creates a new session and returns a JWT token
func (h *AuthHandler) createSessionToken(ctx context.Context, user *auth.User) (string, error) {
	return h.upsertSessionToken(ctx, user, time.Now())
}

// parseAndValidateJWT parses a JWT string, validates the signing method, and returns the subject (user ID).
func (handler *AuthHandler) parseAndValidateJWT(tokenString string) (string, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if token.Method.Alg() != "HS256" {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(handler.jwtSecret), nil
	})
	if err != nil {
		return "", fmt.Errorf("failed to parse token: %w", err)
	}
	if !token.Valid {
		return "", errors.New("invalid token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return "", errors.New("invalid token claims")
	}
	userID, ok := claims["sub"].(string)
	if !ok || userID == "" {
		return "", errors.New("missing user ID in token")
	}
	return userID, nil
}

// validateSessionToken validates a JWT token and retrieves session data from Redis
func (handler *AuthHandler) validateSessionToken(ctx context.Context, tokenString string) (*auth.User, error) {
	if err := handler.ensureRedisConfigured(); err != nil {
		return nil, err
	}

	userID, err := handler.parseAndValidateJWT(tokenString)
	if err != nil {
		return nil, err
	}

	sessionKey := "session:" + userID
	sessionJSON, err := handler.redisClient.Get(ctx, sessionKey).Result()
	if errors.Is(err, redis.Nil) {
		return nil, errors.New("session not found or expired")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve session: %w", err)
	}

	var sessionData SessionData
	if err := json.Unmarshal([]byte(sessionJSON), &sessionData); err != nil {
		return nil, fmt.Errorf("failed to deserialize session data: %w", err)
	}

	return &auth.User{
		ID:        sessionData.UserID,
		Email:     sessionData.Email,
		Name:      sessionData.Name,
		ProjectID: sessionData.ProjectID,
		Role:      sessionData.Role,
		Metadata:  sessionData.Metadata,
	}, nil
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
