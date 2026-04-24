// Package uuidutil provides helpers for UUID conversions.
package uuidutil

import (
	"errors"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
)

// StringToUUID converts a string UUID to pgtype.UUID
func StringToUUID(s string) (pgtype.UUID, error) {
	if s == "" {
		return pgtype.UUID{}, errors.New("empty UUID string")
	}
	parsed, err := uuid.Parse(s)
	if err != nil {
		return pgtype.UUID{}, fmt.Errorf("invalid UUID: %w", err)
	}
	var result pgtype.UUID
	// Scan expects a string, not a uuid.UUID
	if err := result.Scan(parsed.String()); err != nil {
		return pgtype.UUID{}, err
	}
	return result, nil
}

// UUIDToString converts pgtype.UUID to string
func UUIDToString(u pgtype.UUID) string {
	if !u.Valid {
		return ""
	}
	// Convert [16]byte to uuid.UUID then to string
	uuidBytes := u.Bytes
	uuidVal, err := uuid.FromBytes(uuidBytes[:])
	if err != nil {
		return ""
	}
	return uuidVal.String()
}
