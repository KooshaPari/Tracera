// Package validation provides request and field validation helpers.
// Package validation provides input validation helpers.
package validation

import (
	"fmt"
	"regexp"
	"strings"
)

var uuidRegex = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

// ValidateUUID validates UUID format and returns error if invalid
func ValidateUUID(id string) error {
	normalized := NormalizeUUID(id)
	if !uuidRegex.MatchString(normalized) {
		return fmt.Errorf("invalid UUID format: %s", id)
	}
	return nil
}

// NormalizeUUID normalizes UUID to lowercase and trimmed
func NormalizeUUID(id string) string {
	return strings.ToLower(strings.TrimSpace(id))
}

// MustValidateUUID panics if UUID is invalid (use for critical validation)
func MustValidateUUID(id string) {
	if err := ValidateUUID(id); err != nil {
		panic(err)
	}
}

// ValidateUUIDs validates multiple UUIDs and returns first error
func ValidateUUIDs(ids ...string) error {
	for _, id := range ids {
		if err := ValidateUUID(id); err != nil {
			return err
		}
	}
	return nil
}

// IsValidUUID returns boolean indicating if UUID is valid
func IsValidUUID(id string) bool {
	return ValidateUUID(id) == nil
}
