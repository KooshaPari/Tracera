package handlers

import (
	"context"
	"errors"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
)

// Login handles POST /api/v1/auth/login
func (h *AuthHandler) Login(c echo.Context) error {
	ctx := context.Background()

	req := new(LoginRequest)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "invalid request: " + err.Error(),
		})
	}

	if req.Email == "" || req.Password == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "email and password are required",
		})
	}

	if err := h.ensureRedisConfigured(); err != nil {
		log.Printf("Auth login failed: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "authentication service unavailable",
		})
	}

	normalizedEmail := normalizeEmail(req.Email)
	record, err := h.getUserRecordByEmail(ctx, normalizedEmail)
	if err != nil {
		if errors.Is(err, errUserNotFound) {
			return c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error: "invalid credentials",
			})
		}
		log.Printf("Failed to load user record: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "authentication service unavailable",
		})
	}

	if record.PasswordHash == "" {
		log.Printf("User record missing password hash: %s", normalizedEmail)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "authentication service unavailable",
		})
	}

	if !h.passwordHasher.VerifyPassword(record.PasswordHash, req.Password) {
		log.Printf("Invalid password for user: %s", normalizedEmail)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid credentials",
		})
	}

	user := record.toUser()
	token, err := h.createSessionToken(ctx, user)
	if err != nil {
		log.Printf("Failed to create session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to create session",
		})
	}

	h.setAuthCookie(c, token)
	log.Printf("User logged in: %s (%s)", user.Email, user.ID)

	return c.JSON(http.StatusOK, AuthResponse{
		User:        user,
		Token:       token,
		AccessToken: token,
		ExpiresIn:   int64(h.sessionTTL.Seconds()),
	})
}

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
		log.Printf("Failed to validate token: %v", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid or expired token",
		})
	}

	newToken, err := h.extendSession(ctx, user)
	if err != nil {
		log.Printf("Failed to extend session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to refresh session",
		})
	}

	h.setAuthCookie(c, newToken)
	log.Printf("User session refreshed: %s (%s)", user.Email, user.ID)

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
				log.Printf("Warning: Failed to revoke session: %v", err)
			}
			log.Printf("User logged out: %s (%s)", user.Email, user.ID)
		}
	}

	h.clearAuthCookie(echoCtx)
	return echoCtx.JSON(http.StatusOK, map[string]bool{
		"success": true,
	})
}

// Register handles POST /api/v1/auth/register
func (h *AuthHandler) Register(c echo.Context) error {
	ctx := context.Background()

	req, err := h.parseRegisterRequest(c)
	if err != nil || req == nil {
		return err
	}
	if !h.validateRegisterPassword(c, req.Password) {
		return nil
	}

	if err := h.ensureRedisConfigured(); err != nil {
		log.Printf("Auth register failed: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "authentication service unavailable",
		})
	}

	req.Email = normalizeEmail(req.Email)
	exists, err := h.userExists(ctx, req.Email)
	if err != nil {
		log.Printf("Failed to check user existence: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to process registration",
		})
	}
	if exists {
		return c.JSON(http.StatusConflict, ErrorResponse{
			Error: "user already exists",
		})
	}

	user, passwordHash, err := h.createRegisterUser(req)
	if err != nil {
		log.Printf("Failed to hash password: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to process registration",
		})
	}

	if err := h.storeUserRecord(ctx, user, passwordHash); err != nil {
		if errors.Is(err, errUserAlreadyExists) {
			return c.JSON(http.StatusConflict, ErrorResponse{
				Error: "user already exists",
			})
		}
		log.Printf("Failed to store user record: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to process registration",
		})
	}

	token, err := h.createSessionToken(ctx, user)
	if err != nil {
		log.Printf("Failed to create session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to create session",
		})
	}

	h.setAuthCookie(c, token)
	log.Printf("User registered: %s (%s)", user.Email, user.ID)

	return c.JSON(http.StatusCreated, AuthResponse{
		User:        user,
		Token:       token,
		AccessToken: token,
		ExpiresIn:   int64(h.sessionTTL.Seconds()),
	})
}

func (h *AuthHandler) parseRegisterRequest(c echo.Context) (*RegisterRequest, error) {
	req := new(RegisterRequest)
	if err := c.Bind(req); err != nil {
		return nil, c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "invalid request: " + err.Error(),
		})
	}

	if req.Email == "" || req.Password == "" || req.Name == "" {
		return nil, c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "email, password, and name are required",
		})
	}

	return req, nil
}

func (h *AuthHandler) validateRegisterPassword(c echo.Context, password string) bool {
	validationErrors := h.passwordValidator.ValidatePassword(password)
	if len(validationErrors) == 0 {
		return true
	}

	errorMessages := make([]string, len(validationErrors))
	for i, ve := range validationErrors {
		errorMessages[i] = ve.Message
	}

	_ = c.JSON(http.StatusBadRequest, map[string]interface{}{
		"error":    "password does not meet strength requirements",
		"messages": errorMessages,
	})
	return false
}

func (h *AuthHandler) createRegisterUser(req *RegisterRequest) (*auth.User, string, error) {
	hashedPassword, err := h.passwordHasher.HashPassword(req.Password)
	if err != nil {
		return nil, "", err
	}

	user := &auth.User{
		ID:       "user_" + strconv.FormatInt(time.Now().UnixNano(), 10),
		Email:    req.Email,
		Name:     req.Name,
		Role:     "user",
		Metadata: make(map[string]interface{}),
	}

	return user, hashedPassword, nil
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
