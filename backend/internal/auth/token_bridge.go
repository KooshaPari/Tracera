package auth

import (
	"context"
	"crypto/rsa"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"math/big"
	"net/http"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

const (
	hsSecretMinLength     = 32
	jwksCacheTTLDefault   = 24 * time.Hour
	jwksClientTimeout     = 10 * time.Second
	bridgeTokenTTL        = 5 * time.Minute
	bridgeTokenTTLMinutes = 5
	base256Multiplier     = 256
)

// TokenBridge provides bidirectional authentication between HS256 and RS256 tokens
// Handles both WorkOS RS256 tokens (user auth) and internal HS256 service tokens
type TokenBridge struct {
	hsSecret      []byte
	jwksURL       string
	jwksClient    *http.Client
	jwksMutex     sync.RWMutex
	jwksCache     map[string]*rsa.PublicKey
	jwksCacheTime time.Time
	jwksCacheTTL  time.Duration
	audience      string
	issuer        string
}

// Note: WorkOSClaims is already defined in authkit_adapter.go
// Adding a TokenType field would require updating that struct

// JWKSResponse represents the JWKS endpoint response
type JWKSResponse struct {
	Keys []JWK `json:"keys"`
}

// JWK represents a JSON Web Key
type JWK struct {
	Kid string   `json:"kid"`
	Kty string   `json:"kty"`
	Use string   `json:"use"`
	Alg string   `json:"alg"`
	N   string   `json:"n"`
	E   string   `json:"e"`
	X5C []string `json:"x5_c,omitempty"`
}

// NewTokenBridge creates a new token bridge
// hsSecret: Shared HS256 secret for service tokens (min 32 bytes)
// jwksURL: WorkOS JWKS URL for RS256 public keys
// audience: Expected audience claim (typically WorkOS client ID)
// issuer: Expected issuer claim (typically WorkOS API base URL)
func NewTokenBridge(hsSecret []byte, jwksURL, audience, issuer string) (*TokenBridge, error) {
	if len(hsSecret) < hsSecretMinLength {
		return nil, errors.New("HS256 secret must be at least 32 bytes")
	}

	if jwksURL == "" {
		return nil, errors.New("JWKS URL is required")
	}

	tb := &TokenBridge{
		hsSecret:     hsSecret,
		jwksURL:      jwksURL,
		jwksCache:    make(map[string]*rsa.PublicKey),
		jwksCacheTTL: jwksCacheTTLDefault,
		audience:     audience,
		issuer:       issuer,
		jwksClient: &http.Client{
			Timeout: jwksClientTimeout,
		},
	}

	// Fetch JWKS on initialization
	if err := tb.RefreshJWKS(context.Background()); err != nil {
		slog.Error("Warning: Failed to fetch JWKS during initialization", "error", err)
		// Don't fail initialization - JWKS will be fetched on first validation
	}

	return tb, nil
}

// ValidateToken tries RS256 first (user tokens), falls back to HS256 (service tokens)
func (tb *TokenBridge) ValidateToken(ctx context.Context, tokenString string) (*WorkOSClaims, error) {
	// Try RS256 first (WorkOS user tokens)
	claims, err := tb.validateRS256Token(ctx, tokenString)
	if err == nil {
		return claims, nil
	}

	slog.Error("RS256 validation failed , trying HS256...", "error", err)

	// Fall back to HS256 (internal service tokens)
	claims, err = tb.validateHS256Token(tokenString)
	if err != nil {
		return nil, fmt.Errorf("token validation failed for both RS256 and HS256: %w", err)
	}

	return claims, nil
}

// validateRS256Token validates a WorkOS RS256 token using JWKS
func (tb *TokenBridge) validateRS256Token(ctx context.Context, tokenString string) (*WorkOSClaims, error) {
	tb.refreshJWKSIfStale(ctx)

	// Parse token without validation to extract kid
	token, _, err := new(jwt.Parser).ParseUnverified(tokenString, &WorkOSClaims{})
	if err != nil {
		return nil, fmt.Errorf("failed to parse token header: %w", err)
	}

	kid, ok := token.Header["kid"].(string)
	if !ok {
		return nil, errors.New("token missing kid header")
	}

	publicKey, err := tb.getPublicKey(ctx, kid)
	if err != nil {
		return nil, err
	}

	// Parse and validate token
	claims := &WorkOSClaims{}
	parsedToken, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		// Verify signing method is RS256
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return publicKey, nil
	})
	if err != nil {
		return nil, fmt.Errorf("failed to parse RS256 token: %w", err)
	}

	if !parsedToken.Valid {
		return nil, errors.New("invalid RS256 token")
	}

	if err := tb.validateClaims(claims); err != nil {
		return nil, err
	}

	return claims, nil
}

func (tb *TokenBridge) refreshJWKSIfStale(ctx context.Context) {
	tb.jwksMutex.RLock()
	cacheExpired := time.Since(tb.jwksCacheTime) > tb.jwksCacheTTL
	tb.jwksMutex.RUnlock()

	if cacheExpired {
		if err := tb.RefreshJWKS(ctx); err != nil {
			slog.Error("Warning: Failed to refresh JWKS", "error", err)
		}
	}
}

func (tb *TokenBridge) getPublicKey(ctx context.Context, kid string) (interface{}, error) {
	tb.jwksMutex.RLock()
	publicKey, exists := tb.jwksCache[kid]
	tb.jwksMutex.RUnlock()

	if exists {
		return publicKey, nil
	}

	if err := tb.RefreshJWKS(ctx); err != nil {
		return nil, fmt.Errorf("public key not found and JWKS refresh failed: %w", err)
	}

	tb.jwksMutex.RLock()
	publicKey, exists = tb.jwksCache[kid]
	tb.jwksMutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("public key not found for kid: %s", kid)
	}

	return publicKey, nil
}

func (tb *TokenBridge) validateClaims(claims *WorkOSClaims) error {
	if err := tb.validateAudience(claims); err != nil {
		return err
	}
	if err := tb.validateIssuer(claims); err != nil {
		return err
	}
	if err := tb.validateExpiry(claims); err != nil {
		return err
	}

	if claims.Subject == "" && claims.Sub != "" {
		claims.Subject = claims.Sub
	}

	return nil
}

func (tb *TokenBridge) validateAudience(claims *WorkOSClaims) error {
	// WorkOS AuthKit access tokens often omit aud; skip when claim missing.
	if tb.audience == "" || len(claims.Audience) == 0 {
		return nil
	}

	for _, aud := range claims.Audience {
		if aud == tb.audience {
			return nil
		}
	}

	return fmt.Errorf("invalid audience: expected %s, got %v", tb.audience, claims.Audience)
}

func (tb *TokenBridge) validateIssuer(claims *WorkOSClaims) error {
	if tb.issuer == "" || claims.Issuer == tb.issuer {
		return nil
	}

	return fmt.Errorf("invalid issuer: expected %s, got %s", tb.issuer, claims.Issuer)
}

func (tb *TokenBridge) validateExpiry(claims *WorkOSClaims) error {
	if claims.ExpiresAt != nil && claims.ExpiresAt.Before(time.Now()) {
		return fmt.Errorf("token expired at %v", claims.ExpiresAt.Time)
	}
	return nil
}

// validateHS256Token validates an internal HS256 service token
func (tb *TokenBridge) validateHS256Token(tokenString string) (*WorkOSClaims, error) {
	claims := &WorkOSClaims{}
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		// Verify signing method is HS256
		if token.Method.Alg() != "HS256" {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return tb.hsSecret, nil
	})
	if err != nil {
		return nil, fmt.Errorf("failed to parse HS256 token: %w", err)
	}

	if !token.Valid {
		return nil, errors.New("invalid HS256 token")
	}

	// Check expiry
	if claims.ExpiresAt != nil && claims.ExpiresAt.Before(time.Now()) {
		return nil, fmt.Errorf("token expired at %v", claims.ExpiresAt.Time)
	}

	// Service tokens should have type="service"
	if claims.TokenType != "service" {
		slog.Warn("Warning: HS256 token missing type=service claim")
	}

	// Sync RegisteredClaims.Subject from Sub field
	// (JWT parser populates Sub from "sub" claim, but RegisteredClaims.Subject is left empty)
	if claims.Subject == "" && claims.Sub != "" {
		claims.Subject = claims.Sub
	}

	return claims, nil
}

// CreateBridgeToken creates a short-lived HS256 service token (5 min TTL)
func (tb *TokenBridge) CreateBridgeToken(userID, orgID string) (string, error) {
	now := time.Now()
	claims := &WorkOSClaims{
		Sub:       userID,
		OrgID:     orgID,
		TokenType: "service",
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(bridgeTokenTTL)),
			NotBefore: jwt.NewNumericDate(now),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(tb.hsSecret)
	if err != nil {
		return "", fmt.Errorf("failed to sign bridge token: %w", err)
	}

	slog.Info("Created bridge token for user (org ), expires in minutes", "id", userID, "id", orgID, "id", bridgeTokenTTLMinutes)
	return tokenString, nil
}

// RefreshJWKS fetches latest public keys from WorkOS
func (tb *TokenBridge) RefreshJWKS(ctx context.Context) error {
	jwksResp, err := tb.fetchJWKSResponse(ctx)
	if err != nil {
		return err
	}

	newCache := buildRSAKeyCache(jwksResp.Keys)

	if len(newCache) == 0 {
		return errors.New("no valid RSA keys found in JWKS")
	}

	// Update cache
	tb.updateJWKSCache(newCache)

	return nil
}

func (tb *TokenBridge) fetchJWKSResponse(ctx context.Context) (JWKSResponse, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, tb.jwksURL, nil)
	if err != nil {
		return JWKSResponse{}, fmt.Errorf("failed to create JWKS request: %w", err)
	}

	resp, err := tb.jwksClient.Do(req)
	if err != nil {
		return JWKSResponse{}, fmt.Errorf("failed to fetch JWKS: %w", err)
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("failed to close JWKS response body", "error", err)
		}
	}()

	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return JWKSResponse{}, fmt.Errorf("failed to read JWKS response body: %w", err)
		}
		return JWKSResponse{}, fmt.Errorf(
			"JWKS endpoint returned status %d: %s",
			resp.StatusCode,
			string(body),
		)
	}

	var jwksResp JWKSResponse
	if err := json.NewDecoder(resp.Body).Decode(&jwksResp); err != nil {
		return JWKSResponse{}, fmt.Errorf("failed to decode JWKS response: %w", err)
	}

	return jwksResp, nil
}

func buildRSAKeyCache(keys []JWK) map[string]*rsa.PublicKey {
	newCache := make(map[string]*rsa.PublicKey)
	for _, jwk := range keys {
		if jwk.Kty != "RSA" {
			continue
		}

		publicKey, err := parseRSAPublicKey(jwk)
		if err != nil {
			slog.Error("Warning: Failed to parse JWK", "error", jwk.Kid, "error", err)
			continue
		}

		newCache[jwk.Kid] = publicKey
	}

	return newCache
}

func (tb *TokenBridge) updateJWKSCache(newCache map[string]*rsa.PublicKey) {
	tb.jwksMutex.Lock()
	tb.jwksCache = newCache
	tb.jwksCacheTime = time.Now()
	tb.jwksMutex.Unlock()
}

// parseRSAPublicKey converts a JWK to an RSA public key
func parseRSAPublicKey(jwk JWK) (*rsa.PublicKey, error) {
	// Decode modulus (n) - base64url encoded
	nBytes, err := base64.RawURLEncoding.DecodeString(jwk.N)
	if err != nil {
		return nil, fmt.Errorf("failed to decode modulus: %w", err)
	}

	// Decode exponent (e) - base64url encoded
	eBytes, err := base64.RawURLEncoding.DecodeString(jwk.E)
	if err != nil {
		return nil, fmt.Errorf("failed to decode exponent: %w", err)
	}

	// Convert modulus to big.Int
	modulus := new(big.Int).SetBytes(nBytes)

	// Convert exponent to int
	// The exponent is typically AQAB (65537) which fits in an int
	exponent := 0
	for _, byteValue := range eBytes {
		exponent = exponent*base256Multiplier + int(byteValue)
	}

	return &rsa.PublicKey{
		N: modulus,
		E: exponent,
	}, nil
}

// Close cleans up resources
func (tb *TokenBridge) Close() error {
	tb.jwksClient.CloseIdleConnections()
	return nil
}
