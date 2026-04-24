package cliproxy

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

const (
	cliProxyReadTimeout      = 30 * time.Second
	cliProxyWriteTimeout     = 30 * time.Second
	cliProxyShutdownTimeout  = 5 * time.Second
	cliProxyDefaultInputTok  = 100
	cliProxyDefaultOutputTok = 50

	anthropicProviderType = "anthropic"
	codexProviderType     = "codex"
	openAIProviderType    = "openai"
)

// Config holds CLIProxy configuration
type Config struct {
	Host            string
	Port            int
	Providers       []ProviderConfig
	DefaultProvider string
}

// ProviderConfig holds OAuth configuration for a specific AI provider
type ProviderConfig struct {
	Name         string
	Type         string // anthropicProviderType, openAIProviderType, codexProviderType
	ClientID     string
	ClientSecret string
	RedirectURI  string
	BaseURL      string
}

// Service wraps the embedded CLIProxy functionality
type Service struct {
	config *Config
	echo   *echo.Echo
	server *http.Server
}

// NewService creates a new CLIProxy service with the given configuration
func NewService(cfg *Config) (*Service, error) {
	if cfg == nil {
		return nil, errors.New("config cannot be nil")
	}

	echoServer := echo.New()
	echoServer.HideBanner = true
	echoServer.Use(middleware.RequestLogger())
	echoServer.Use(middleware.Recover())
	echoServer.Use(middleware.CORS())

	service := &Service{
		config: cfg,
		echo:   echoServer,
	}

	// Register routes
	service.registerRoutes()

	return service, nil
}

// registerRoutes sets up the CLIProxy endpoints
func (service *Service) registerRoutes() {
	// Health check
	service.echo.GET("/health", service.handleHealth)

	// OAuth endpoints
	oauth := service.echo.Group("/oauth")
	oauth.GET("/authorize", service.handleAuthorize)
	oauth.GET("/callback", service.handleCallback)
	oauth.POST("/token", service.handleToken)
	oauth.POST("/refresh", service.handleRefresh)

	// API proxy endpoints (Anthropic-compatible)
	api := service.echo.Group("/v1")
	api.POST("/messages", service.handleMessages)
	api.POST("/chat/completions", service.handleChatCompletions) // OpenAI-compatible endpoint
}

// Run starts the CLIProxy HTTP server
func (service *Service) Run(ctx context.Context) error {
	addr := service.config.Host + ":" + strconv.Itoa(service.config.Port)

	service.server = &http.Server{
		Addr:         addr,
		Handler:      service.echo,
		ReadTimeout:  cliProxyReadTimeout,
		WriteTimeout: cliProxyWriteTimeout,
	}

	slog.Info("🔐 CLIProxy service starting on", "name", addr)

	// Start server in goroutine
	errChan := make(chan error, 1)
	go func() {
		if err := service.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			errChan <- err
		}
	}()

	// Wait for context cancellation or error
	select {
	case <-ctx.Done():
		slog.Info("🔐 CLIProxy service shutting down...")
		// Use context.Background() with timeout for graceful shutdown.
		// context.WithoutCancel(ctx) is also fine but context.Background() is more explicit for linter.
		shutdownCtx, cancel := context.WithTimeout(context.Background(), cliProxyShutdownTimeout)
		defer cancel()
		return service.server.Shutdown(shutdownCtx) //nolint:contextcheck // Use fresh context for shutdown
	case err := <-errChan:
		return fmt.Errorf("CLIProxy server error: %w", err)
	}
}

// Shutdown gracefully stops the CLIProxy service
func (service *Service) Shutdown(ctx context.Context) error {
	if service.server != nil {
		return service.server.Shutdown(ctx)
	}
	return nil
}

// GetEndpoint returns the base endpoint URL for the CLIProxy service
func (service *Service) GetEndpoint() string {
	return "http://" + service.config.Host + ":" + strconv.Itoa(service.config.Port)
}

// Health check handler
func (service *Service) handleHealth(echoCtx echo.Context) error {
	return echoCtx.JSON(http.StatusOK, map[string]interface{}{
		"status":    "healthy",
		"service":   "cliproxy",
		"providers": service.getProviderNames(),
	})
}

// OAuth authorize handler - redirects to provider OAuth
func (service *Service) handleAuthorize(echoCtx echo.Context) error {
	provider := echoCtx.QueryParam("provider")
	if provider == "" {
		provider = service.config.DefaultProvider
	}

	providerCfg := service.getProvider(provider)
	if providerCfg == nil {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown provider: "+provider)
	}

	// Build OAuth authorization URL
	authURL := service.buildAuthURL(providerCfg, echoCtx.QueryParam("state"))

	return echoCtx.Redirect(http.StatusTemporaryRedirect, authURL)
}

// OAuth callback handler - exchanges code for token
func (service *Service) handleCallback(echoCtx echo.Context) error {
	code := echoCtx.QueryParam("code")
	state := echoCtx.QueryParam("state")
	provider := echoCtx.QueryParam("provider")

	if code == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "missing authorization code")
	}

	if provider == "" {
		provider = service.config.DefaultProvider
	}

	providerCfg := service.getProvider(provider)
	if providerCfg == nil {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown provider: "+provider)
	}

	// Exchange code for access token
	token, err := service.exchangeCodeForToken(providerCfg, code)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return echoCtx.JSON(http.StatusOK, map[string]interface{}{
		"access_token": token,
		"provider":     provider,
		"state":        state,
	})
}

// Token endpoint for manual token exchange
func (service *Service) handleToken(echoCtx echo.Context) error {
	var req struct {
		Code     string `json:"code"`
		Provider string `json:"provider"`
	}

	if err := echoCtx.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	return service.handleTokenResponse(echoCtx, req.Provider, func(providerCfg *ProviderConfig) (string, error) {
		return service.exchangeCodeForToken(providerCfg, req.Code)
	})
}

// Refresh token endpoint
func (service *Service) handleRefresh(echoCtx echo.Context) error {
	var req struct {
		RefreshToken string `json:"refresh_token"`
		Provider     string `json:"provider"`
	}

	if err := echoCtx.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	return service.handleTokenResponse(echoCtx, req.Provider, func(providerCfg *ProviderConfig) (string, error) {
		return service.refreshAccessToken(providerCfg, req.RefreshToken)
	})
}

func (service *Service) resolveProvider(provider string) (*ProviderConfig, string, error) {
	providerName := provider
	if providerName == "" {
		providerName = service.config.DefaultProvider
	}

	providerCfg := service.getProvider(providerName)
	if providerCfg == nil {
		return nil, "", echo.NewHTTPError(http.StatusBadRequest, "unknown provider: "+providerName)
	}

	return providerCfg, providerName, nil
}

func (service *Service) handleTokenResponse(
	echoCtx echo.Context,
	provider string,
	tokenFn func(*ProviderConfig) (string, error),
) error {
	providerCfg, providerName, err := service.resolveProvider(provider)
	if err != nil {
		return err
	}

	token, err := tokenFn(providerCfg)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return echoCtx.JSON(http.StatusOK, map[string]interface{}{
		"access_token": token,
		"provider":     providerName,
	})
}

// Messages endpoint (Anthropic-compatible)
func (service *Service) handleMessages(echoCtx echo.Context) error {
	// Extract bearer token from Authorization header
	authHeader := echoCtx.Request().Header.Get("Authorization")
	if authHeader == "" {
		return echo.NewHTTPError(http.StatusUnauthorized, "missing authorization token")
	}

	// Parse request body
	var req map[string]interface{}
	if err := echoCtx.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Determine provider from token or model
	provider := service.determineProvider(req)

	// Forward request to actual AI provider
	resp, err := service.forwardRequest(provider, authHeader, req)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadGateway, err.Error())
	}

	return echoCtx.JSON(http.StatusOK, resp)
}

// Chat completions endpoint (OpenAI-compatible)
func (service *Service) handleChatCompletions(echoCtx echo.Context) error {
	// Extract bearer token
	authHeader := echoCtx.Request().Header.Get("Authorization")
	if authHeader == "" {
		return echo.NewHTTPError(http.StatusUnauthorized, "missing authorization token")
	}

	// Parse request
	var req map[string]interface{}
	if err := echoCtx.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Convert to Anthropic format and forward
	provider := service.determineProvider(req)
	anthropicReq := service.convertToAnthropicFormat(req)

	resp, err := service.forwardRequest(provider, authHeader, anthropicReq)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadGateway, err.Error())
	}

	// Convert back to OpenAI format if needed
	openaiResp := service.convertToOpenAIFormat(resp)

	return echoCtx.JSON(http.StatusOK, openaiResp)
}

// Helper: Get provider config by name
func (service *Service) getProvider(name string) *ProviderConfig {
	for i := range service.config.Providers {
		if service.config.Providers[i].Name == name {
			return &service.config.Providers[i]
		}
	}
	return nil
}

// Helper: Get all provider names
func (service *Service) getProviderNames() []string {
	names := make([]string, len(service.config.Providers))
	for i, p := range service.config.Providers {
		names[i] = p.Name
	}
	return names
}

// Helper: Build OAuth authorization URL
func (service *Service) buildAuthURL(provider *ProviderConfig, state string) string {
	// This is a placeholder - actual implementation depends on provider
	// For Anthropic: would use their OAuth endpoints
	// For OpenAI: would use their OAuth endpoints
	baseURL := provider.BaseURL
	if baseURL == "" {
		// Default OAuth endpoints by provider type
		switch provider.Type {
		case anthropicProviderType:
			baseURL = "https://api.anthropic.com/oauth/authorize"
		case openAIProviderType, codexProviderType:
			baseURL = "https://auth.openai.com/authorize"
		default:
			baseURL = "https://example.com/oauth/authorize"
		}
	}

	return fmt.Sprintf("%s?client_id=%s&redirect_uri=%s&response_type=code&state=%s",
		baseURL, provider.ClientID, provider.RedirectURI, state)
}

// Helper: Exchange authorization code for access token
func (service *Service) exchangeCodeForToken(provider *ProviderConfig, _ string) (string, error) {
	// This is a placeholder - actual implementation would make HTTP request to provider's token endpoint
	// For now, return a mock token
	slog.Info("Exchanging code for token with provider", "id", provider.Name)
	return "mock_access_token_" + provider.Name, nil
}

// Helper: Refresh access token
func (service *Service) refreshAccessToken(provider *ProviderConfig, _ string) (string, error) {
	// Placeholder - actual implementation would make HTTP request to provider's refresh endpoint
	slog.Info("Refreshing token with provider", "id", provider.Name)
	return "mock_refreshed_token_" + provider.Name, nil
}

// Helper: Determine provider from request
func (service *Service) determineProvider(req map[string]interface{}) string {
	// Check if model is specified
	if model, ok := req["model"].(string); ok {
		// Map model to provider
		if model == "gpt-5.2-codex" {
			return codexProviderType
		}
		if model == "claude-sonnet-4" || model == "claude-opus-4" {
			return "claude"
		}
	}

	// Default to configured default provider
	return service.config.DefaultProvider
}

// Helper: Forward request to actual AI provider
func (service *Service) forwardRequest(
	provider string,
	_ string,
	req map[string]interface{},
) (map[string]interface{}, error) {
	// Placeholder - actual implementation would make HTTP request to provider API
	slog.Info("Forwarding request to provider", "id", provider)

	// Mock response
	return map[string]interface{}{
		"id":   "msg_mock_123",
		"type": "message",
		"role": "assistant",
		"content": []map[string]interface{}{
			{
				"type": "text",
				"text": "This is a mock response from CLIProxy",
			},
		},
		"model":       req["model"],
		"stop_reason": "end_turn",
		"usage": map[string]interface{}{
			"input_tokens":  cliProxyDefaultInputTok,
			"output_tokens": cliProxyDefaultOutputTok,
		},
	}, nil
}

// Helper: Convert OpenAI format to Anthropic format
func (service *Service) convertToAnthropicFormat(req map[string]interface{}) map[string]interface{} {
	// Placeholder - actual implementation would convert message formats
	return req
}

// Helper: Convert Anthropic format to OpenAI format
func (service *Service) convertToOpenAIFormat(resp map[string]interface{}) map[string]interface{} {
	// Placeholder - actual implementation would convert response formats
	return resp
}
