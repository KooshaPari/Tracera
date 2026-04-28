package handlers

import (
	"context"
	"errors"
	"log/slog"
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// Refresh handles POST /api/v1/auth/refresh
func (h *AuthHandler) Refresh(c echo.Context) error {
	ctx := context.Background()

	tokenString, err := h.extractAuthToken(c)
	if err != nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "missing authentication token",
		})
	}

	user, err := h.validateSessionToken(ctx, tokenString)
	if err != nil {
		slog.Error("Failed to validate token", "error", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid or expired token",
		})
	}

	newToken, err := h.extendSession(ctx, user)
	if err != nil {
		slog.Error("Failed to extend session", "error", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to refresh session",
		})
	}

	h.setAuthCookie(c, newToken)
	slog.Info("User session refreshed ( )", "user", user.Email, "id", user.ID)

	return c.JSON(http.StatusOK, AuthResponse{
		User:        user,
		Token:       newToken,
		AccessToken: newToken,
		ExpiresIn:   int64(h.sessionTTL.Seconds()),
	})
}

// Logout handles POST /api/v1/auth/logout
func (h *AuthHandler) Logout(echoCtx echo.Context) error {
	ctx := context.Background()

	tokenString, err := h.extractAuthToken(echoCtx)
	if err == nil && tokenString != "" {
		user, err := h.validateSessionToken(ctx, tokenString)
		if err == nil && user != nil {
			sessionKey := "session:" + user.ID
			if err := h.redisClient.Del(ctx, sessionKey).Err(); err != nil {
				slog.Error("Warning: Failed to revoke session", "error", err)
			}
			slog.Info("User logged out ( )", "user", user.Email, "id", user.ID)
		}
	}

	h.clearAuthCookie(echoCtx)
	return echoCtx.JSON(http.StatusOK, map[string]bool{
		"success": true,
	})
}

// GetUser retrieves the current authenticated user from context
func (h *AuthHandler) GetUser(c echo.Context) error {
	user, ok := c.Get("user").(*auth.User)
	if !ok || user == nil {
		tokenString, err := h.extractAuthToken(c)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error: "unauthenticated",
			})
		}

		loadedUser, err := h.validateSessionToken(c.Request().Context(), tokenString)
		if err != nil {
			return c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error: "unauthenticated",
			})
		}
		user = loadedUser
	}
	return c.JSON(http.StatusOK, user)
}

// VerifyToken verifies an authentication token
func (h *AuthHandler) VerifyToken(echoCtx echo.Context) error {
	ctx := context.Background()

	token := echoCtx.QueryParam("token")
	if token == "" {
		authHeader := echoCtx.Request().Header.Get("Authorization")
		if authHeader != "" && len(authHeader) > 7 && authHeader[:7] == "Bearer " {
			token = authHeader[7:]
		}
	}

	if token == "" {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "token is required",
		})
	}

	user, err := h.validateSessionToken(ctx, token)
	if err != nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid or expired token",
		})
	}

	return echoCtx.JSON(http.StatusOK, user)
}

func (h *AuthHandler) extractAuthToken(c echo.Context) (string, error) {
	token, err := c.Cookie("auth_token")
	if err == nil && token.Value != "" {
		return token.Value, nil
	}

	authHeader := c.Request().Header.Get("Authorization")
	if authHeader != "" && len(authHeader) > 7 && authHeader[:7] == "Bearer " {
		return authHeader[7:], nil
	}

	return "", errors.New("missing authentication token")
}
