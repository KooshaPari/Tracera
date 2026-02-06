package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
)

const (
	defaultSessionHours = 24
	defaultSessionTTL   = defaultSessionHours * time.Hour
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
		authProvider:      authProvider,
		redisClient:       redisClient,
		jwtSecret:         jwtSecret,
		sessionTTL:        sessionTTL,
		isProduction:      isProduction,
		passwordHasher:    auth.NewPasswordHasher(),
		passwordValidator: auth.NewPasswordStrengthValidator(),
	}
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
	User  *auth.User `json:"user"`
	Token string     `json:"token"`
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

// Login handles POST /api/v1/auth/login
// Validates credentials and creates a session
// @Summary User login
// @Description Authenticate user with email and password
// @Tags auth
// @Accept json
// @Produce json
// @Param request body LoginRequest true "Login credentials"
// @Success 200 {object} AuthResponse "Login successful"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 401 {object} ErrorResponse "Invalid credentials"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/auth/login [post]
func (h *AuthHandler) Login(c echo.Context) error {
	ctx := context.Background()

	// Parse request
	req := new(LoginRequest)
	if err := c.Bind(req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "invalid request: " + err.Error(),
		})
	}

	// Validate input
	if req.Email == "" || req.Password == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "email and password are required",
		})
	}

	// In a real implementation, you would validate credentials against a user database
	// For now, we generate a JWT token that would have been issued by WorkOS
	// This is a temporary implementation until WorkOS API integration is complete

	// Generate a mock JWT token (in production, this would come from WorkOS)
	// We'll create a token that the authProvider can validate
	// TODO: Once database schema supports password storage, implement actual password verification
	user, err := h.generateMockAuthToken(ctx, req.Email)
	if err != nil {
		log.Printf("Failed to generate auth token: %v", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid credentials",
		})
	}

	// Create session in Redis
	token, err := h.createSessionToken(ctx, user)
	if err != nil {
		log.Printf("Failed to create session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to create session",
		})
	}

	// Set HttpOnly cookie
	h.setAuthCookie(c, token)

	log.Printf("User logged in: %s (%s)", user.Email, user.ID)

	return c.JSON(http.StatusOK, AuthResponse{
		User:  user,
		Token: token,
	})
}

// Refresh handles POST /api/v1/auth/refresh
// Validates and refreshes an existing session
// @Summary Refresh authentication token
// @Description Refresh expired or expiring authentication token
// @Tags auth
// @Accept json
// @Produce json
// @Success 200 {object} AuthResponse "Token refreshed successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 401 {object} ErrorResponse "Unauthorized"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/auth/refresh [post]
func (h *AuthHandler) Refresh(c echo.Context) error {
	ctx := context.Background()

	// Get token from cookie
	token, err := c.Cookie("auth_token")
	if err != nil || token.Value == "" {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "missing authentication token",
		})
	}

	// Validate token and get user
	user, err := h.validateSessionToken(ctx, token.Value)
	if err != nil {
		log.Printf("Failed to validate token: %v", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid or expired token",
		})
	}

	// Extend session in Redis
	newToken, err := h.extendSession(ctx, user)
	if err != nil {
		log.Printf("Failed to extend session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to refresh session",
		})
	}

	// Set new HttpOnly cookie
	h.setAuthCookie(c, newToken)

	log.Printf("User session refreshed: %s (%s)", user.Email, user.ID)

	return c.JSON(http.StatusOK, AuthResponse{
		User:  user,
		Token: newToken,
	})
}

// Logout handles POST /api/v1/auth/logout
// Revokes the current session
// @Summary User logout
// @Description Logout and revoke session
// @Tags auth
// @Accept json
// @Produce json
// @Success 200 {object} map[string]bool "Logout successful"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/auth/logout [post]
func (h *AuthHandler) Logout(echoCtx echo.Context) error {
	ctx := context.Background()

	// Get token from cookie
	token, err := echoCtx.Cookie("auth_token")
	if err == nil && token.Value != "" {
		// Try to revoke session from Redis
		// Extract user ID from token to delete session
		user, err := h.validateSessionToken(ctx, token.Value)
		if err == nil && user != nil {
			sessionKey := "session:" + user.ID
			if err := h.redisClient.Del(ctx, sessionKey).Err(); err != nil {
				log.Printf("Warning: Failed to revoke session: %v", err)
			}
			log.Printf("User logged out: %s (%s)", user.Email, user.ID)
		}
	}

	// Clear cookie (set expired)
	h.clearAuthCookie(echoCtx)

	return echoCtx.JSON(http.StatusOK, map[string]bool{
		"success": true,
	})
}

// Register handles POST /api/v1/auth/register
// Creates a new user with password validation and hashing
// @Summary User registration
// @Description Register a new user with email, password, and name
// @Tags auth
// @Accept json
// @Produce json
// @Param request body RegisterRequest true "Registration credentials"
// @Success 201 {object} AuthResponse "Registration successful"
// @Failure 400 {object} ErrorResponse "Invalid request or weak password"
// @Failure 409 {object} ErrorResponse "User already exists"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /api/v1/auth/register [post]
func (h *AuthHandler) Register(c echo.Context) error {
	ctx := context.Background()

	req, err := h.parseRegisterRequest(c)
	if err != nil {
		return err
	}
	if err := h.validateRegisterPassword(c, req.Password); err != nil {
		return err
	}

	user, err := h.createRegisterUser(req)
	if err != nil {
		log.Printf("Failed to hash password: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to process registration",
		})
	}

	// Create session in Redis
	token, err := h.createSessionToken(ctx, user)
	if err != nil {
		log.Printf("Failed to create session: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to create session",
		})
	}

	// Set HttpOnly cookie
	h.setAuthCookie(c, token)

	log.Printf("User registered: %s (%s)", user.Email, user.ID)

	return c.JSON(http.StatusCreated, AuthResponse{
		User:  user,
		Token: token,
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

func (h *AuthHandler) validateRegisterPassword(c echo.Context, password string) error {
	validationErrors := h.passwordValidator.ValidatePassword(password)
	if len(validationErrors) == 0 {
		return nil
	}

	errorMessages := make([]string, len(validationErrors))
	for i, ve := range validationErrors {
		errorMessages[i] = ve.Message
	}

	return c.JSON(http.StatusBadRequest, map[string]interface{}{
		"error":    "password does not meet strength requirements",
		"messages": errorMessages,
	})
}

func (h *AuthHandler) createRegisterUser(req *RegisterRequest) (*auth.User, error) {
	hashedPassword, err := h.passwordHasher.HashPassword(req.Password)
	if err != nil {
		return nil, err
	}

	// TODO: Once database schema supports password storage, implement user creation
	// For now, create a mock user for demonstration
	user := &auth.User{
		ID:       "user_" + strconv.FormatInt(time.Now().UnixNano(), 10),
		Email:    req.Email,
		Name:     req.Name,
		Role:     "user",
		Metadata: make(map[string]interface{}),
	}

	// Store hashedPassword in metadata (would be in database in production)
	user.Metadata["password_hash"] = hashedPassword

	return user, nil
}

// createSessionToken creates a new session and returns a JWT token
func (h *AuthHandler) createSessionToken(ctx context.Context, user *auth.User) (string, error) {
	return h.upsertSessionToken(ctx, user, time.Now())
}

// validateSessionToken validates a JWT token and retrieves session data from Redis
func (handler *AuthHandler) validateSessionToken(ctx context.Context, tokenString string) (*auth.User, error) {
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

// generateMockAuthToken generates a mock user for testing
// In production, this would be replaced with WorkOS/AuthKit validation
func (h *AuthHandler) generateMockAuthToken(_ context.Context, email string) (*auth.User, error) {
	// For now, create a mock user object
	// In production, this would validate against WorkOS AuthKit API
	// and the authProvider would sync the profile from WorkOS

	user := &auth.User{
		ID:        "user_" + strconv.FormatInt(time.Now().UnixNano(), 10),
		Email:     email,
		Name:      email,
		Role:      "user",
		ProjectID: "",
		Metadata:  make(map[string]interface{}),
	}

	return user, nil
}

// GetUser retrieves the current authenticated user from context
// @Summary Get current user
// @Description Get the current authenticated user information
// @Tags auth
// @Accept json
// @Produce json
// @Success 200 {object} auth.User "Current user"
// @Failure 401 {object} ErrorResponse "Unauthenticated"
// @Router /api/v1/auth/me [get]
func (h *AuthHandler) GetUser(c echo.Context) error {
	user, ok := c.Get("user").(*auth.User)
	if !ok || user == nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "unauthenticated",
		})
	}
	return c.JSON(http.StatusOK, user)
}

// VerifyToken verifies an authentication token
// This is useful for validating tokens from external sources
// @Summary Verify authentication token
// @Description Verify if an authentication token is valid
// @Tags auth
// @Accept json
// @Produce json
// @Param token query string true "Token to verify"
// @Success 200 {object} auth.User "Token is valid"
// @Failure 401 {object} ErrorResponse "Invalid token"
// @Router /api/v1/auth/verify [get]
func (h *AuthHandler) VerifyToken(echoCtx echo.Context) error {
	ctx := context.Background()

	// Get token from query parameter or Authorization header
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

	// Validate token
	user, err := h.validateSessionToken(ctx, token)
	if err != nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid or expired token",
		})
	}

	return echoCtx.JSON(http.StatusOK, user)
}
