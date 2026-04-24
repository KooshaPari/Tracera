package auth

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/stretchr/testify/require"
)

// TestJWTSecret is the secret key used for testing JWT tokens
const TestJWTSecret = "test-secret-key-for-auth-testing-only"

// TestClientID is the WorkOS Client ID used for testing JWKS URL construction
const TestClientID = "client_test_123456789"

// CreateValidWorkOSToken creates a valid WorkOS JWT token for testing
func CreateValidWorkOSToken(t *testing.T) string {
	t.Helper()

	claims := &WorkOSClaims{
		Sub:           "user_01H8XYZ123",
		Email:         "test@example.com",
		EmailVerified: true,
		Name:          "Test User",
		GivenName:     "Test",
		FamilyName:    "User",
		Picture:       "https://example.com/avatar.jpg",
		OrgID:         "org_01H8ABC456",
		OrgSlug:       "test-org",
		Role:          "admin",
		Permissions:   []string{"read:items", "write:items"},
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(TestJWTSecret))
	require.NoError(t, err, "Failed to create test token")

	return tokenString
}

// CreateExpiredWorkOSToken creates an expired WorkOS JWT token for testing
func CreateExpiredWorkOSToken(t *testing.T) string {
	t.Helper()

	claims := &WorkOSClaims{
		Sub:           "user_01H8XYZ123",
		Email:         "test@example.com",
		EmailVerified: true,
		Name:          "Test User",
		OrgID:         "org_01H8ABC456",
		OrgSlug:       "test-org",
		Role:          "user",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(-1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now().Add(-2 * time.Hour)),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(TestJWTSecret))
	require.NoError(t, err, "Failed to create expired test token")

	return tokenString
}

// CreateTokenWithInvalidSignature creates a token signed with wrong secret
func CreateTokenWithInvalidSignature(t *testing.T) string {
	t.Helper()

	claims := &WorkOSClaims{
		Sub:           "user_01H8XYZ123",
		Email:         "test@example.com",
		EmailVerified: true,
		Name:          "Test User",
		OrgID:         "org_01H8ABC456",
		OrgSlug:       "test-org",
		Role:          "user",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("wrong-secret-key"))
	require.NoError(t, err, "Failed to create test token with invalid signature")

	return tokenString
}

// CreateTokenWithWrongSigningMethod creates a token using RS256 instead of HS256
func CreateTokenWithWrongSigningMethod(t *testing.T) string {
	t.Helper()

	claims := &WorkOSClaims{
		Sub:           "user_01H8XYZ123",
		Email:         "test@example.com",
		EmailVerified: true,
		Name:          "Test User",
		OrgID:         "org_01H8ABC456",
		OrgSlug:       "test-org",
		Role:          "user",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodNone, claims)
	tokenString, err := token.SignedString(jwt.UnsafeAllowNoneSignatureType)
	require.NoError(t, err, "Failed to create token with none signing method")

	return tokenString
}

// CreateCustomWorkOSToken creates a token with custom claims for testing
func CreateCustomWorkOSToken(t *testing.T, customClaims *WorkOSClaims) string {
	t.Helper()

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, customClaims)
	tokenString, err := token.SignedString([]byte(TestJWTSecret))
	require.NoError(t, err, "Failed to create custom test token")

	return tokenString
}

// CreateMalformedToken creates an invalid JWT token string
func CreateMalformedToken(t *testing.T) string {
	t.Helper()
	return "not.a.valid.jwt.token.format"
}

// MockProfileData represents mock database profile data
type MockProfileData struct {
	ID           string
	AuthID       string
	WorkosUserID string
	WorkosOrgID  string
	Email        string
	FullName     string
	AvatarURL    string
	Metadata     map[string]interface{}
}

// DefaultMockProfile returns a default mock profile for testing
func DefaultMockProfile() *MockProfileData {
	return &MockProfileData{
		ID:           "550e8400-e29b-41d4-a716-446655440000",
		AuthID:       "user_01H8XYZ123",
		WorkosUserID: "user_01H8XYZ123",
		WorkosOrgID:  "org_01H8ABC456",
		Email:        "test@example.com",
		FullName:     "Test User",
		AvatarURL:    "https://example.com/avatar.jpg",
		Metadata: map[string]interface{}{
			"department": "engineering",
			"role":       "developer",
		},
	}
}

// MetadataToJSON converts metadata map to JSON bytes for database mocking
func MetadataToJSON(t *testing.T, metadata map[string]interface{}) []byte {
	t.Helper()

	if metadata == nil {
		return []byte("{}")
	}

	jsonBytes, err := json.Marshal(metadata)
	require.NoError(t, err, "Failed to marshal metadata to JSON")

	return jsonBytes
}

// MockWorkOSClaims returns mock WorkOS claims for testing
func MockWorkOSClaims() *WorkOSClaims {
	return &WorkOSClaims{
		Sub:           "user_01H8XYZ123",
		Email:         "test@example.com",
		EmailVerified: true,
		Name:          "Test User",
		GivenName:     "Test",
		FamilyName:    "User",
		Picture:       "https://example.com/avatar.jpg",
		OrgID:         "org_01H8ABC456",
		OrgSlug:       "test-org",
		Role:          "admin",
		Permissions:   []string{"read:items", "write:items"},
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
}

// MinimalWorkOSClaims returns minimal valid WorkOS claims
func MinimalWorkOSClaims() *WorkOSClaims {
	return &WorkOSClaims{
		Sub:   "user_minimal",
		Email: "minimal@example.com",
		Name:  "Minimal User",
		OrgID: "org_minimal",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}
}

// CreateTokenFromClaims creates a JWT token from WorkOSClaims
func CreateTokenFromClaims(t *testing.T, claims *WorkOSClaims, secret string) string {
	t.Helper()

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(secret))
	require.NoError(t, err, "Failed to create token from claims")

	return tokenString
}

// AssertUserEquals compares two User objects for equality
func AssertUserEquals(t *testing.T, expected, actual *User, msgAndArgs ...interface{}) {
	t.Helper()

	require.NotNil(t, actual, "User should not be nil")
	require.Equal(t, expected.ID, actual.ID, msgAndArgs...)
	require.Equal(t, expected.Email, actual.Email, msgAndArgs...)
	require.Equal(t, expected.Name, actual.Name, msgAndArgs...)
	require.Equal(t, expected.Role, actual.Role, msgAndArgs...)
	require.Equal(t, expected.ProjectID, actual.ProjectID, msgAndArgs...)

	// Compare metadata if both exist
	if expected.Metadata != nil && actual.Metadata != nil {
		require.Equal(t, expected.Metadata, actual.Metadata, msgAndArgs...)
	}
}

// CreateMultipleMockProfiles creates multiple mock profiles for list testing
func CreateMultipleMockProfiles(count int) []*MockProfileData {
	profiles := make([]*MockProfileData, count)

	for index := 0; index < count; index++ {
		profiles[index] = &MockProfileData{
			ID:           "550e8400-e29b-41d4-a716-44665544000" + string(rune('0'+index)),
			AuthID:       "user_" + string(rune('0'+index)),
			WorkosUserID: "user_" + string(rune('0'+index)),
			WorkosOrgID:  "org_test",
			Email:        "user" + string(rune('0'+index)) + "@example.com",
			FullName:     "Test User " + string(rune('0'+index)),
			AvatarURL:    "https://example.com/avatar" + string(rune('0'+index)) + ".jpg",
			Metadata: map[string]interface{}{
				"index": index,
			},
		}
	}

	return profiles
}
