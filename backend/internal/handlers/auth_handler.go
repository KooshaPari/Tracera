package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
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

	if err := h.ensureRedisConfigured(); err != nil {
		log.Printf("Auth login failed: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "authentication service unavailable",
		})
	}

	normalizedEmail := normalizeEmail(req.Email)
	record, err := h.getUserRecordByEmail(ctx, normalizedEmail)
	if err != nil {
		log.Printf("Failed to load user record: %v", err)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid credentials",
		})
	}

	if !h.passwordHasher.VerifyPassword(record.PasswordHash, req.Password) {
		log.Printf("Invalid password for user: %s", normalizedEmail)
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "invalid credentials",
		})
	}

	user := record.toUser()

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
		User:        user,
		Token:       token,
		AccessToken: token,
		ExpiresIn:   int64(h.sessionTTL.Seconds()),
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

	tokenString, err := h.extractAuthToken(c)
	if err != nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error: "missing authentication token",
		})
	}

	// Validate token and get user
	user, err := h.validateSessionToken(ctx, tokenString)
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
		User:        user,
		Token:       newToken,
		AccessToken: newToken,
		ExpiresIn:   int64(h.sessionTTL.Seconds()),
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

	// Get token from cookie or Authorization header
	tokenString, err := h.extractAuthToken(echoCtx)
	if err == nil && tokenString != "" {
		// Try to revoke session from Redis
		// Extract user ID from token to delete session
		user, err := h.validateSessionToken(ctx, tokenString)
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
