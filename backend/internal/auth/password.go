package auth

import (
	"errors"
	"fmt"
	"regexp"
	"unicode"

	"golang.org/x/crypto/bcrypt"
)

const (
	defaultPasswordWorkFactor = 12
	defaultPasswordMinLength  = 8
)

// PasswordHasher provides password hashing and verification functionality
type PasswordHasher struct {
	workFactor int
}

// NewPasswordHasher creates a new password hasher with secure defaults
func NewPasswordHasher() *PasswordHasher {
	return &PasswordHasher{
		workFactor: defaultPasswordWorkFactor, // Balance between security and performance
	}
}

// PasswordStrengthValidator validates password strength requirements
type PasswordStrengthValidator struct {
	minLength      int
	requireUpper   bool
	requireLower   bool
	requireNumbers bool
	requireSpecial bool
}

// NewPasswordStrengthValidator creates a new validator with secure defaults
func NewPasswordStrengthValidator() *PasswordStrengthValidator {
	return &PasswordStrengthValidator{
		minLength:      defaultPasswordMinLength,
		requireUpper:   true,
		requireLower:   true,
		requireNumbers: true,
		requireSpecial: true,
	}
}

// ValidationError represents a password validation error
type ValidationError struct {
	Field   string
	Message string
}

// ValidatePassword checks if a password meets strength requirements
func (validator *PasswordStrengthValidator) ValidatePassword(password string) []ValidationError {
	var errors []ValidationError

	// Check minimum length
	if len(password) < validator.minLength {
		errors = append(errors, ValidationError{
			Field:   "password_length",
			Message: fmt.Sprintf("password must be at least %d characters long", validator.minLength),
		})
	}

	// Check for uppercase letters
	if validator.requireUpper && !containsUppercase(password) {
		errors = append(errors, ValidationError{
			Field:   "password_uppercase",
			Message: "password must contain at least one uppercase letter",
		})
	}

	// Check for lowercase letters
	if validator.requireLower && !containsLowercase(password) {
		errors = append(errors, ValidationError{
			Field:   "password_lowercase",
			Message: "password must contain at least one lowercase letter",
		})
	}

	// Check for numbers
	if validator.requireNumbers && !containsNumber(password) {
		errors = append(errors, ValidationError{
			Field:   "password_number",
			Message: "password must contain at least one number",
		})
	}

	// Check for special characters
	if validator.requireSpecial && !containsSpecial(password) {
		errors = append(errors, ValidationError{
			Field:   "password_special",
			Message: "password must contain at least one special character (!@#$%^&*)",
		})
	}

	return errors
}

// HashPassword hashes a password using bcrypt
// Returns the hashed password or an error if hashing fails
func (hasher *PasswordHasher) HashPassword(password string) (string, error) {
	if password == "" {
		return "", errors.New("password cannot be empty")
	}

	hashedPassword, err := bcrypt.GenerateFromPassword(
		[]byte(password),
		hasher.workFactor,
	)
	if err != nil {
		return "", fmt.Errorf("failed to hash password: %w", err)
	}

	return string(hashedPassword), nil
}

// VerifyPassword verifies a password against its hash
// Returns true if the password matches, false otherwise
func (p *PasswordHasher) VerifyPassword(hashedPassword, password string) bool {
	if hashedPassword == "" || password == "" {
		return false
	}

	err := bcrypt.CompareHashAndPassword(
		[]byte(hashedPassword),
		[]byte(password),
	)
	return err == nil
}

// Helper functions for password validation

func containsUppercase(s string) bool {
	for _, r := range s {
		if unicode.IsUpper(r) {
			return true
		}
	}
	return false
}

func containsLowercase(s string) bool {
	for _, r := range s {
		if unicode.IsLower(r) {
			return true
		}
	}
	return false
}

func containsNumber(s string) bool {
	for _, r := range s {
		if unicode.IsDigit(r) {
			return true
		}
	}
	return false
}

func containsSpecial(s string) bool {
	// Match any special character from the allowed set
	specialRegex := regexp.MustCompile(`[!@#$%^&*()_+=\-\[\]{};:'"<>,.?/\\|~` + "`]")
	return specialRegex.MatchString(s)
}
