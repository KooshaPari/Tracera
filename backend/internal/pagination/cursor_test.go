package pagination

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEncodeCursor(t *testing.T) {
	tests := []struct {
		name      string
		id        string
		timestamp time.Time
		wantEmpty bool
	}{
		{
			name:      "valid cursor",
			id:        "123e4567-e89b-12d3-a456-426614174000",
			timestamp: time.Unix(1234567890, 0),
			wantEmpty: false,
		},
		{
			name:      "empty id",
			id:        "",
			timestamp: time.Unix(1234567890, 0),
			wantEmpty: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cursor := EncodeCursor(tt.id, tt.timestamp)
			if tt.wantEmpty {
				assert.Empty(t, cursor)
			} else {
				assert.NotEmpty(t, cursor)
			}
		})
	}
}

func TestDecodeCursor(t *testing.T) {
	tests := []struct {
		name      string
		cursor    string
		wantID    string
		wantTime  time.Time
		wantError bool
		wantNil   bool
	}{
		{
			name:      "valid cursor",
			cursor:    EncodeCursor("123e4567-e89b-12d3-a456-426614174000", time.Unix(1234567890, 0)),
			wantID:    "123e4567-e89b-12d3-a456-426614174000",
			wantTime:  time.Unix(1234567890, 0),
			wantError: false,
			wantNil:   false,
		},
		{
			name:      "empty cursor",
			cursor:    "",
			wantError: false,
			wantNil:   true,
		},
		{
			name:      "invalid base64",
			cursor:    "not-valid-base64!!!",
			wantError: true,
			wantNil:   false,
		},
		{
			name:      "invalid format - no separator",
			cursor:    EncodeCursor("invalid", time.Unix(1234567890, 0))[:10], // truncated
			wantError: true,
			wantNil:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cursor, err := DecodeCursor(tt.cursor)

			if tt.wantError {
				assert.Error(t, err)
				return
			}

			require.NoError(t, err)

			if tt.wantNil {
				assert.Nil(t, cursor)
			} else {
				require.NotNil(t, cursor)
				assert.Equal(t, tt.wantID, cursor.ID)
				assert.Equal(t, tt.wantTime.Unix(), cursor.Timestamp.Unix())
			}
		})
	}
}

func TestEncodeDecode_RoundTrip(t *testing.T) {
	id := "123e4567-e89b-12d3-a456-426614174000"
	timestamp := time.Unix(1234567890, 0)

	encoded := EncodeCursor(id, timestamp)
	decoded, err := DecodeCursor(encoded)

	require.NoError(t, err)
	require.NotNil(t, decoded)
	assert.Equal(t, id, decoded.ID)
	assert.Equal(t, timestamp.Unix(), decoded.Timestamp.Unix())
}

type cursorPaginationCase struct {
	name         string
	cursor       string
	limit        int
	defaultLimit int
	maxLimit     int
	wantCursor   string
	wantLimit    int
	wantError    bool
}

func cursorPaginationCases() []cursorPaginationCase {
	cursorValue := EncodeCursor("test-id", time.Unix(1234567890, 0))
	return append(validCursorCases(cursorValue), invalidCursorCases()...)
}

func validCursorCases(cursorValue string) []cursorPaginationCase {
	return []cursorPaginationCase{
		{
			name:         "valid params",
			cursor:       cursorValue,
			limit:        25,
			defaultLimit: 50,
			maxLimit:     100,
			wantCursor:   cursorValue,
			wantLimit:    25,
			wantError:    false,
		},
		{
			name:         "empty cursor",
			cursor:       "",
			limit:        25,
			defaultLimit: 50,
			maxLimit:     100,
			wantCursor:   "",
			wantLimit:    25,
			wantError:    false,
		},
		{
			name:         "zero limit uses default",
			cursor:       "",
			limit:        0,
			defaultLimit: 50,
			maxLimit:     100,
			wantCursor:   "",
			wantLimit:    50,
			wantError:    false,
		},
		{
			name:         "negative limit uses default",
			cursor:       "",
			limit:        -10,
			defaultLimit: 50,
			maxLimit:     100,
			wantCursor:   "",
			wantLimit:    50,
			wantError:    false,
		},
		{
			name:         "limit exceeds max",
			cursor:       "",
			limit:        150,
			defaultLimit: 50,
			maxLimit:     100,
			wantCursor:   "",
			wantLimit:    100,
			wantError:    false,
		},
	}
}

func invalidCursorCases() []cursorPaginationCase {
	return []cursorPaginationCase{
		{
			name:         "invalid cursor",
			cursor:       "invalid-cursor",
			limit:        25,
			defaultLimit: 50,
			maxLimit:     100,
			wantError:    true,
		},
	}
}

func runCursorPaginationCase(t *testing.T, tt cursorPaginationCase) {
	t.Helper()
	cursor, limit, err := ParseCursorPaginationParams(
		tt.cursor,
		tt.limit,
		tt.defaultLimit,
		tt.maxLimit,
	)

	if tt.wantError {
		assert.Error(t, err)
		return
	}

	require.NoError(t, err)
	assert.Equal(t, tt.wantCursor, cursor)
	assert.Equal(t, tt.wantLimit, limit)
}

func TestParseCursorPaginationParams(t *testing.T) {
	for _, tt := range cursorPaginationCases() {
		t.Run(tt.name, func(t *testing.T) {
			runCursorPaginationCase(t, tt)
		})
	}
}
