package valueobjects

import (
	"errors"
	"fmt"
	"regexp"
	"strings"
)

// Email represents a validated email address.
//
// Email is a value object that ensures all email addresses are valid
// at the time of creation. Invalid emails cannot be created.
//
// # Design
//
//   - Immutable: No setters, fields are private
//   - Validated: Email format is validated at creation
//   - Normalized: Local part is lowercased
type Email struct {
	localPart string
	domain    string
}

// emailRegex validates basic email format.
// More strict validation should be done by the domain.
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

// ErrInvalidEmail is returned when email format is invalid.
var ErrInvalidEmail = errors.New("invalid email format")

// NewEmail creates a new Email value object after validating the format.
//
// Returns ErrInvalidEmail if the email is not valid.
func NewEmail(address string) (*Email, error) {
	address = strings.TrimSpace(address)
	if address == "" {
		return nil, fmt.Errorf("%w: empty email", ErrInvalidEmail)
	}

	if !emailRegex.MatchString(address) {
		return nil, fmt.Errorf("%w: %s", ErrInvalidEmail, address)
	}

	parts := strings.SplitN(address, "@", 2)
	return &Email{
		localPart: strings.ToLower(parts[0]),
		domain:    strings.ToLower(parts[1]),
	}, nil
}

// LocalPart returns the local part of the email (before @).
func (e *Email) LocalPart() string {
	return e.localPart
}

// Domain returns the domain part of the email (after @).
func (e *Email) Domain() string {
	return e.domain
}

// String returns the full email address.
func (e *Email) String() string {
	return e.localPart + "@" + e.domain
}

// MarshalText implements encoding.TextMarshaler.
func (e *Email) MarshalText() ([]byte, error) {
	return []byte(e.String()), nil
}

// UnmarshalText implements encoding.TextUnmarshaler.
func (e *Email) UnmarshalText(text []byte) error {
	email, err := NewEmail(string(text))
	if err != nil {
		return err
	}
	*e = *email
	return nil
}

// Equals checks if two Email value objects are equal.
func (e *Email) Equals(other *Email) bool {
	if other == nil {
		return false
	}
	return e.localPart == other.localPart && e.domain == other.domain
}

// Compare compares two emails.
// Returns -1 if e < other, 0 if e == other, 1 if e > other.
func (e *Email) Compare(other *Email) int {
	if e.domain != other.domain {
		if e.domain < other.domain {
			return -1
		}
		return 1
	}
	if e.localPart < other.localPart {
		return -1
	}
	if e.localPart > other.localPart {
		return 1
	}
	return 0
}

// IsDisposable checks if the email is from a known disposable domain.
func (e *Email) IsDisposable() bool {
	disposableDomains := map[string]bool{
		"tempmail.com":      true,
		"throwaway.email":   true,
		"guerrillamail.com": true,
		"mailinator.com":    true,
	}
	return disposableDomains[e.domain]
}

// Format returns a formatted version of the email.
// Use %s for full email, %l for local part, %d for domain.
func (e *Email) Format(format string) string {
	format = strings.ReplaceAll(format, "%s", e.String())
	format = strings.ReplaceAll(format, "%l", e.localPart)
	format = strings.ReplaceAll(format, "%d", e.domain)
	return format
}
