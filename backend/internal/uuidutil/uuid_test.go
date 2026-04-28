package uuidutil

import (
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test constants
const (
	testValidUUID = "550e8400-e29b-41d4-a716-446655440000"
)

// TestStringToUUID_Success tests converting a valid UUID string
func TestStringToUUID_Success(t *testing.T) {
	validUUID := testValidUUID

	result, err := StringToUUID(validUUID)

	require.NoError(t, err)
	assert.True(t, result.Valid)
	assert.Equal(t, validUUID, UUIDToString(result))
}

// TestStringToUUID_EmptyString tests that empty string returns error
func TestStringToUUID_EmptyString(t *testing.T) {
	_, err := StringToUUID("")

	require.Error(t, err)
	assert.Equal(t, "empty UUID string", err.Error())
}

// TestStringToUUID_InvalidUUID tests that invalid UUID returns error
func TestStringToUUID_InvalidUUID(t *testing.T) {
	invalidUUIDs := []string{
		"not-a-uuid",
		"550e8400-e29b-41d4",
		"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
		"12345678-1234-1234-1234-123456789012-extra",
	}

	for _, invalidUUID := range invalidUUIDs {
		_, err := StringToUUID(invalidUUID)
		require.Error(t, err, "should error for invalid UUID: %s", invalidUUID)
	}
}

// TestUUIDToString_Success tests converting pgtype.UUID to string
func TestUUIDToString_Success(t *testing.T) {
	validUUIDStr := testValidUUID
	pgUUID, err := StringToUUID(validUUIDStr)
	require.NoError(t, err)

	result := UUIDToString(pgUUID)

	assert.Equal(t, validUUIDStr, result)
}

// TestUUIDToString_Invalid tests that invalid pgtype.UUID returns empty string
func TestUUIDToString_Invalid(t *testing.T) {
	invalidUUID := pgtype.UUID{Valid: false}

	result := UUIDToString(invalidUUID)

	assert.Empty(t, result)
}

// TestUUIDToString_ValidButZero tests edge case of valid UUID that's all zeros
func TestUUIDToString_ValidButZero(t *testing.T) {
	zeroUUID := uuid.Nil
	var pgUUID pgtype.UUID
	err := pgUUID.Scan(zeroUUID.String())
	require.NoError(t, err)

	result := UUIDToString(pgUUID)

	assert.Equal(t, "00000000-0000-0000-0000-000000000000", result)
}

// TestRoundTrip_StringToUUIDAndBack tests converting string to UUID and back
func TestRoundTrip_StringToUUIDAndBack(t *testing.T) {
	testCases := []string{
		testValidUUID,
		"123e4567-e89b-12d3-a456-426614174000",
		"00000000-0000-0000-0000-000000000000",
		uuid.New().String(),
	}

	for _, originalUUID := range testCases {
		t.Run(originalUUID, func(t *testing.T) {
			pgUUID, err := StringToUUID(originalUUID)
			require.NoError(t, err)

			result := UUIDToString(pgUUID)

			assert.Equal(t, originalUUID, result)
		})
	}
}

// TestStringToUUID_CaseInsensitive tests UUID parsing with different cases
func TestStringToUUID_CaseInsensitive(t *testing.T) {
	lowercaseUUID := testValidUUID
	uppercaseUUID := "550E8400-E29B-41D4-A716-446655440000"

	result1, err1 := StringToUUID(lowercaseUUID)
	require.NoError(t, err1)

	result2, err2 := StringToUUID(uppercaseUUID)
	require.NoError(t, err2)

	// Both should produce the same result
	assert.Equal(t, UUIDToString(result1), UUIDToString(result2))
}

// TestStringToUUID_GeneratedUUID tests with newly generated UUIDs
func TestStringToUUID_GeneratedUUID(t *testing.T) {
	generated := uuid.New()
	uuidStr := generated.String()

	result, err := StringToUUID(uuidStr)

	require.NoError(t, err)
	assert.Equal(t, uuidStr, UUIDToString(result))
}

// TestUUIDToString_Consistency tests multiple calls return same result
func TestUUIDToString_Consistency(t *testing.T) {
	validUUIDStr := testValidUUID
	pgUUID, err := StringToUUID(validUUIDStr)
	require.NoError(t, err)

	result1 := UUIDToString(pgUUID)
	result2 := UUIDToString(pgUUID)
	result3 := UUIDToString(pgUUID)

	assert.Equal(t, result1, result2)
	assert.Equal(t, result2, result3)
	assert.Equal(t, validUUIDStr, result1)
}

// TestStringToUUID_WithoutHyphens tests UUID parsing without hyphens works
func TestStringToUUID_WithoutHyphens(t *testing.T) {
	// Google uuid library actually accepts UUIDs without hyphens
	uuidWithoutHyphens := "550e8400e29b41d4a716446655440000"

	result, err := StringToUUID(uuidWithoutHyphens)

	require.NoError(t, err)
	assert.True(t, result.Valid)
	// Should convert to standard format with hyphens
	assert.Equal(t, testValidUUID, UUIDToString(result))
}

// TestStringToUUID_PartiallyValid tests partially valid UUID formats
func TestStringToUUID_PartiallyValid(t *testing.T) {
	testCases := []struct {
		name  string
		input string
		valid bool
	}{
		{"valid", testValidUUID, true},
		{"missing segment", "550e8400-e29b-41d4-a716", false},
		{"extra segment", "550e8400-e29b-41d4-a716-446655440000-extra", false},
		{"wrong separator", "550e8400.e29b.41d4.a716.446655440000", false},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			_, err := StringToUUID(tc.input)
			if tc.valid {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
			}
		})
	}
}
