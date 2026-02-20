package auth

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	// Test password for hashing and verification tests
	testSecurePassword = "SecurePassword123!"
)

type passwordHasherCase struct {
	name string
	run  func(t *testing.T, hasher *PasswordHasher)
}

func passwordHasherHashCases() []passwordHasherCase {
	return []passwordHasherCase{
		{
			name: "HashPassword generates valid bcrypt hash",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash, err := hasher.HashPassword(testSecurePassword)

				require.NoError(t, err)
				assert.NotEmpty(t, hash)
				assert.True(t, strings.HasPrefix(hash, "$2a$") || strings.HasPrefix(hash, "$2b$"))
			},
		},
		{
			name: "HashPassword fails with empty password",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash, err := hasher.HashPassword("")

				require.Error(t, err)
				assert.Empty(t, hash)
				assert.Equal(t, "password cannot be empty", err.Error())
			},
		},
	}
}

func passwordHasherVerifyCases() []passwordHasherCase {
	return []passwordHasherCase{
		{
			name: "VerifyPassword matches correct password",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)

				isValid := hasher.VerifyPassword(hash, testSecurePassword)
				assert.True(t, isValid)
			},
		},
		{
			name: "VerifyPassword rejects incorrect password",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)

				isValid := hasher.VerifyPassword(hash, "WrongPassword456!")
				assert.False(t, isValid)
			},
		},
		{
			name: "VerifyPassword rejects empty password",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)

				isValid := hasher.VerifyPassword(hash, "")
				assert.False(t, isValid)
			},
		},
		{
			name: "VerifyPassword rejects empty hash",
			run: func(t *testing.T, hasher *PasswordHasher) {
				isValid := hasher.VerifyPassword("", testSecurePassword)
				assert.False(t, isValid)
			},
		},
	}
}

func passwordHasherSaltCases() []passwordHasherCase {
	return []passwordHasherCase{
		{
			name: "Different passwords produce different hashes",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash1, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)
				hash2, err := hasher.HashPassword("DifferentPassword456!")
				require.NoError(t, err)

				assert.NotEqual(t, hash1, hash2)
			},
		},
		{
			name: "Same password produces different hashes (due to salt)",
			run: func(t *testing.T, hasher *PasswordHasher) {
				hash1, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)
				hash2, err := hasher.HashPassword(testSecurePassword)
				require.NoError(t, err)

				assert.NotEqual(t, hash1, hash2)
				assert.True(t, hasher.VerifyPassword(hash1, testSecurePassword))
				assert.True(t, hasher.VerifyPassword(hash2, testSecurePassword))
			},
		},
	}
}

func passwordHasherCases() []passwordHasherCase {
	return append(
		append(passwordHasherHashCases(), passwordHasherVerifyCases()...),
		passwordHasherSaltCases()...,
	)
}

func TestPasswordHasher(t *testing.T) {
	hasher := NewPasswordHasher()

	for _, tc := range passwordHasherCases() {
		t.Run(tc.name, func(t *testing.T) {
			tc.run(t, hasher)
		})
	}
}

type passwordValidationCase struct {
	name          string
	password      string
	wantError     bool
	expectedField string
	minErrorCount int
}

func passwordValidationCases() []passwordValidationCase {
	return []passwordValidationCase{
		{
			name:      "Valid strong password passes validation",
			password:  testSecurePassword,
			wantError: false,
		},
		{
			name:          "Password too short fails validation",
			password:      "Pass1!",
			wantError:     true,
			expectedField: "password_length",
		},
		{
			name:          "Password missing uppercase fails validation",
			password:      "securepassword123!",
			wantError:     true,
			expectedField: "password_uppercase",
		},
		{
			name:          "Password missing lowercase fails validation",
			password:      "SECUREPASSWORD123!",
			wantError:     true,
			expectedField: "password_lowercase",
		},
		{
			name:          "Password missing numbers fails validation",
			password:      "SecurePassword!",
			wantError:     true,
			expectedField: "password_number",
		},
		{
			name:          "Password missing special character fails validation",
			password:      "SecurePassword123",
			wantError:     true,
			expectedField: "password_special",
		},
		{
			name:          "Password with multiple validation errors",
			password:      "weak",
			wantError:     true,
			minErrorCount: 2,
		},
	}
}

func runPasswordValidationCase(t *testing.T, validator *PasswordStrengthValidator, tc passwordValidationCase) {
	t.Helper()
	errors := validator.ValidatePassword(tc.password)

	if !tc.wantError {
		assert.Empty(t, errors)
		return
	}

	assert.NotEmpty(t, errors)
	if tc.minErrorCount > 0 {
		assert.GreaterOrEqual(t, len(errors), tc.minErrorCount)
	}

	if tc.expectedField == "" {
		return
	}

	foundExpectedError := false
	for _, err := range errors {
		if err.Field == tc.expectedField {
			foundExpectedError = true
			break
		}
	}
	assert.True(t, foundExpectedError, "Expected to find error for field %s", tc.expectedField)
}

func specialCharacterPasswords() []string {
	return []string{
		testSecurePassword,
		"SecurePassword123@",
		"SecurePassword123#",
		"SecurePassword123$",
		"SecurePassword123%",
		"SecurePassword123^",
		"SecurePassword123&",
		"SecurePassword123*",
	}
}

func TestPasswordStrengthValidator(t *testing.T) {
	validator := NewPasswordStrengthValidator()

	for _, tc := range passwordValidationCases() {
		t.Run(tc.name, func(t *testing.T) {
			runPasswordValidationCase(t, validator, tc)
		})
	}

	t.Run("Password with various special characters passes validation", func(t *testing.T) {
		for _, password := range specialCharacterPasswords() {
			errors := validator.ValidatePassword(password)
			assert.Empty(t, errors, "Password %s should pass validation", password)
		}
	})
}

func BenchmarkHashPassword(b *testing.B) {
	hasher := NewPasswordHasher()
	password := testSecurePassword

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if _, err := hasher.HashPassword(password); err != nil {
			b.Fatalf("HashPassword failed: %v", err)
		}
	}
}

func BenchmarkVerifyPassword(b *testing.B) {
	hasher := NewPasswordHasher()
	password := testSecurePassword
	hash, err := hasher.HashPassword(password)
	require.NoError(b, err)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = hasher.VerifyPassword(hash, password)
	}
}
