// Package pagination provides cursor encoding and parsing helpers.
package pagination

import (
	"encoding/base64"
	"fmt"
	"strconv"
	"strings"
	"time"
)

const cursorPartsCount = 2

// Cursor represents pagination cursor data
type Cursor struct {
	ID        string
	Timestamp time.Time
}

// EncodeCursor creates a base64-encoded cursor from an ID and timestamp
func EncodeCursor(id string, timestamp time.Time) string {
	data := id + ":" + strconv.FormatInt(timestamp.Unix(), 10)
	return base64.URLEncoding.EncodeToString([]byte(data))
}

// DecodeCursor parses a base64-encoded cursor into ID and timestamp
func DecodeCursor(cursor string) (*Cursor, error) {
	if cursor == "" {
		return nil, nil
	}

	decoded, err := base64.URLEncoding.DecodeString(cursor)
	if err != nil {
		return nil, fmt.Errorf("invalid cursor format: %w", err)
	}

	parts := strings.Split(string(decoded), ":")
	if len(parts) != cursorPartsCount {
		return nil, fmt.Errorf("invalid cursor format: expected %d parts, got %d", cursorPartsCount, len(parts))
	}

	timestamp, err := strconv.ParseInt(parts[1], 10, 64)
	if err != nil {
		return nil, fmt.Errorf("invalid cursor timestamp: %w", err)
	}

	return &Cursor{
		ID:        parts[0],
		Timestamp: time.Unix(timestamp, 0),
	}, nil
}

// CursorPaginationRequest represents common cursor pagination parameters
type CursorPaginationRequest struct {
	Cursor string `query:"cursor"`
	Limit  int    `query:"limit"`
}

// CursorPaginationResponse represents cursor pagination metadata
type CursorPaginationResponse struct {
	NextCursor string `json:"next_cursor,omitempty"`
	HasMore    bool   `json:"has_more"`
	Count      int    `json:"count"`
}

// ParseCursorPaginationParams extracts and validates cursor pagination parameters
func ParseCursorPaginationParams(cursor string, limit int, defaultLimit int, maxLimit int) (string, int, error) {
	// Validate and set limit
	if limit <= 0 {
		limit = defaultLimit
	}
	if limit > maxLimit {
		limit = maxLimit
	}

	// Validate cursor if provided
	if cursor != "" {
		_, err := DecodeCursor(cursor)
		if err != nil {
			return "", 0, fmt.Errorf("invalid cursor: %w", err)
		}
	}

	return cursor, limit, nil
}
