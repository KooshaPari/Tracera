package env

import (
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	envTestDurationShort = 5 * time.Second
	envTestDurationLong  = 10 * time.Second
	envTestInterval      = 1 * time.Minute
	envTestPeriod        = 1 * time.Hour
	envTestDurationTiny  = 100 * time.Millisecond
)

// TestNew creates a new manager
func TestNew(t *testing.T) {
	manager := New()

	assert.NotNil(t, manager)
	assert.NotNil(t, manager.vars)
}

// TestLoad loads environment variables
func TestLoad(t *testing.T) {
	// Set a test variable
	_ = os.Setenv("TEST_ENV_VAR", "test_value")
	defer func() {
		_ = os.Unsetenv("TEST_ENV_VAR")
	}()

	manager := New()
	manager.Load()

	assert.Equal(t, "test_value", manager.Get("TEST_ENV_VAR"))
}

// TestGet retrieves a string variable
func TestGet(t *testing.T) {
	manager := New()
	manager.Set("TEST_KEY", "test_value")

	result := manager.Get("TEST_KEY")

	assert.Equal(t, "test_value", result)
	_ = os.Unsetenv("TEST_KEY")
}

// TestGet_NotSet returns empty string for unset variable
func TestGet_NotSet(t *testing.T) {
	manager := New()

	result := manager.Get("NONEXISTENT_VAR")

	assert.Equal(t, "", result)
}

// TestGetRequired returns value when set
func TestGetRequired_Set(t *testing.T) {
	manager := New()
	manager.Set("REQUIRED_VAR", "required_value")

	result, err := manager.GetRequired("REQUIRED_VAR")

	assert.NoError(t, err)
	assert.Equal(t, "required_value", result)
	_ = os.Unsetenv("REQUIRED_VAR")
}

// TestGetRequired returns error when not set
func TestGetRequired_NotSet(t *testing.T) {
	manager := New()

	result, err := manager.GetRequired("MISSING_REQUIRED_VAR")

	assert.Error(t, err)
	assert.Equal(t, "", result)
	assert.Contains(t, err.Error(), "required environment variable")
}

// TestGetOrDefault returns value when set
func TestGetOrDefault_Set(t *testing.T) {
	manager := New()
	manager.Set("DEFAULT_VAR", "actual_value")

	result := manager.GetOrDefault("DEFAULT_VAR", "default_value")

	assert.Equal(t, "actual_value", result)
	_ = os.Unsetenv("DEFAULT_VAR")
}

// TestGetOrDefault returns default when not set
func TestGetOrDefault_NotSet(t *testing.T) {
	manager := New()

	result := manager.GetOrDefault("MISSING_VAR", "default_value")

	assert.Equal(t, "default_value", result)
}

// TestGetInt retrieves integer variable
func TestGetInt_Valid(t *testing.T) {
	manager := New()
	manager.Set("INT_VAR", "42")

	result, err := manager.GetInt("INT_VAR")

	assert.NoError(t, err)
	assert.Equal(t, 42, result)
	_ = os.Unsetenv("INT_VAR")
}

// TestGetInt returns error for invalid integer
func TestGetInt_Invalid(t *testing.T) {
	manager := New()
	manager.Set("INT_VAR", "not_a_number")

	result, err := manager.GetInt("INT_VAR")

	assert.Error(t, err)
	assert.Equal(t, 0, result)
	assert.Contains(t, err.Error(), "not a valid integer")
	_ = os.Unsetenv("INT_VAR")
}

// TestGetInt returns error when not set
func TestGetInt_NotSet(t *testing.T) {
	manager := New()

	result, err := manager.GetInt("MISSING_INT_VAR")

	assert.Error(t, err)
	assert.Equal(t, 0, result)
	assert.Contains(t, err.Error(), "not set")
}

// TestGetIntOrDefault returns value when set
func TestGetIntOrDefault_Set(t *testing.T) {
	manager := New()
	manager.Set("INT_DEFAULT_VAR", "99")

	result := manager.GetIntOrDefault("INT_DEFAULT_VAR", 42)

	assert.Equal(t, 99, result)
	_ = os.Unsetenv("INT_DEFAULT_VAR")
}

// TestGetIntOrDefault returns default when invalid
func TestGetIntOrDefault_Invalid(t *testing.T) {
	manager := New()
	manager.Set("INT_DEFAULT_VAR", "not_a_number")

	result := manager.GetIntOrDefault("INT_DEFAULT_VAR", 42)

	assert.Equal(t, 42, result)
	_ = os.Unsetenv("INT_DEFAULT_VAR")
}

// TestGetBool retrieves boolean variable
func TestGetBool_Valid(t *testing.T) {
	testCases := []struct {
		input    string
		expected bool
	}{
		{"true", true},
		{"false", false},
		{"1", true},
		{"0", false},
		{"t", true},
		{"f", false},
		{"T", true},
		{"F", false},
	}

	for _, tc := range testCases {
		t.Run(tc.input, func(t *testing.T) {
			manager := New()
			manager.Set("BOOL_VAR", tc.input)

			result, err := manager.GetBool("BOOL_VAR")

			assert.NoError(t, err)
			assert.Equal(t, tc.expected, result)
			_ = os.Unsetenv("BOOL_VAR")
		})
	}
}

// TestGetBool returns error for invalid boolean
func TestGetBool_Invalid(t *testing.T) {
	manager := New()
	manager.Set("BOOL_VAR", "not_a_bool")

	result, err := manager.GetBool("BOOL_VAR")

	assert.Error(t, err)
	assert.False(t, result)
	assert.Contains(t, err.Error(), "not a valid boolean")
	_ = os.Unsetenv("BOOL_VAR")
}

// TestGetBool returns error when not set
func TestGetBool_NotSet(t *testing.T) {
	manager := New()

	result, err := manager.GetBool("MISSING_BOOL_VAR")

	assert.Error(t, err)
	assert.False(t, result)
	assert.Contains(t, err.Error(), "not set")
}

// TestGetBoolOrDefault returns value when set
func TestGetBoolOrDefault_Set(t *testing.T) {
	manager := New()
	manager.Set("BOOL_DEFAULT_VAR", "true")

	result := manager.GetBoolOrDefault("BOOL_DEFAULT_VAR", false)

	assert.True(t, result)
	_ = os.Unsetenv("BOOL_DEFAULT_VAR")
}

// TestGetBoolOrDefault returns default when invalid
func TestGetBoolOrDefault_Invalid(t *testing.T) {
	manager := New()
	manager.Set("BOOL_DEFAULT_VAR", "not_a_bool")

	result := manager.GetBoolOrDefault("BOOL_DEFAULT_VAR", true)

	assert.True(t, result)
	_ = os.Unsetenv("BOOL_DEFAULT_VAR")
}

// TestGetDuration retrieves duration variable
func TestGetDuration_Valid(t *testing.T) {
	testCases := []struct {
		input    string
		expected time.Duration
	}{
		{"5s", envTestDurationShort},
		{"1m", envTestInterval},
		{"1h", envTestPeriod},
		{"100ms", envTestDurationTiny},
	}

	for _, tc := range testCases {
		t.Run(tc.input, func(t *testing.T) {
			manager := New()
			manager.Set("DURATION_VAR", tc.input)

			result, err := manager.GetDuration("DURATION_VAR")

			assert.NoError(t, err)
			assert.Equal(t, tc.expected, result)
			_ = os.Unsetenv("DURATION_VAR")
		})
	}
}

// TestGetDuration returns error for invalid duration
func TestGetDuration_Invalid(t *testing.T) {
	manager := New()
	manager.Set("DURATION_VAR", "not_a_duration")

	result, err := manager.GetDuration("DURATION_VAR")

	assert.Error(t, err)
	assert.Equal(t, time.Duration(0), result)
	assert.Contains(t, err.Error(), "not a valid duration")
	_ = os.Unsetenv("DURATION_VAR")
}

// TestGetDuration returns error when not set
func TestGetDuration_NotSet(t *testing.T) {
	manager := New()

	result, err := manager.GetDuration("MISSING_DURATION_VAR")

	assert.Error(t, err)
	assert.Equal(t, time.Duration(0), result)
	assert.Contains(t, err.Error(), "not set")
}

// TestGetDurationOrDefault returns value when set
func TestGetDurationOrDefault_Set(t *testing.T) {
	manager := New()
	manager.Set("DURATION_DEFAULT_VAR", "10s")

	result := manager.GetDurationOrDefault("DURATION_DEFAULT_VAR", envTestDurationShort)

	assert.Equal(t, envTestDurationLong, result)
	_ = os.Unsetenv("DURATION_DEFAULT_VAR")
}

// TestGetDurationOrDefault returns default when invalid
func TestGetDurationOrDefault_Invalid(t *testing.T) {
	manager := New()
	manager.Set("DURATION_DEFAULT_VAR", "not_a_duration")

	result := manager.GetDurationOrDefault("DURATION_DEFAULT_VAR", envTestDurationShort)

	assert.Equal(t, envTestDurationShort, result)
	_ = os.Unsetenv("DURATION_DEFAULT_VAR")
}

// TestSet sets environment variable
func TestSet(t *testing.T) {
	manager := New()

	manager.Set("SET_VAR", "set_value")

	assert.Equal(t, "set_value", manager.Get("SET_VAR"))
	assert.Equal(t, "set_value", os.Getenv("SET_VAR"))
	_ = os.Unsetenv("SET_VAR")
}

// TestValidate returns no error when all required vars are set
func TestValidate_AllSet(t *testing.T) {
	manager := New()
	manager.Set("VAR1", "value1")
	manager.Set("VAR2", "value2")
	manager.Set("VAR3", "value3")

	err := manager.Validate([]string{"VAR1", "VAR2", "VAR3"})

	assert.NoError(t, err)
	_ = os.Unsetenv("VAR1")
	_ = os.Unsetenv("VAR2")
	_ = os.Unsetenv("VAR3")
}

// TestValidate returns error when required vars are missing
func TestValidate_Missing(t *testing.T) {
	manager := New()
	manager.Set("VAR1", "value1")

	err := manager.Validate([]string{"VAR1", "VAR2", "VAR3"})

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "missing required environment variables")
	assert.Contains(t, err.Error(), "VAR2")
	assert.Contains(t, err.Error(), "VAR3")
	_ = os.Unsetenv("VAR1")
}

// TestValidate returns no error for empty required list
func TestValidate_Empty(t *testing.T) {
	manager := New()

	err := manager.Validate([]string{})

	assert.NoError(t, err)
}

// TestMultipleOperations tests sequence of operations
func TestMultipleOperations(t *testing.T) {
	manager := New()

	// Set multiple vars
	manager.Set("KEY1", "value1")
	manager.Set("KEY2", "100")
	manager.Set("KEY3", "true")

	// Retrieve them
	assert.Equal(t, "value1", manager.Get("KEY1"))
	val, err := manager.GetInt("KEY2")
	require.NoError(t, err)
	assert.Equal(t, 100, val)
	boolVal, err := manager.GetBool("KEY3")
	require.NoError(t, err)
	assert.True(t, boolVal)

	// Validate
	err = manager.Validate([]string{"KEY1", "KEY2", "KEY3"})
	assert.NoError(t, err)

	// Cleanup
	_ = os.Unsetenv("KEY1")
	_ = os.Unsetenv("KEY2")
	_ = os.Unsetenv("KEY3")
}

// TestZeroValues tests handling of empty/zero values
func TestZeroValues(t *testing.T) {
	manager := New()

	// Test empty string
	manager.Set("EMPTY_STRING", "")
	assert.Equal(t, "", manager.Get("EMPTY_STRING"))

	// Test zero int
	manager.Set("ZERO_INT", "0")
	val, err := manager.GetInt("ZERO_INT")
	assert.NoError(t, err)
	assert.Equal(t, 0, val)

	// Test false bool
	manager.Set("FALSE_BOOL", "false")
	boolVal, err := manager.GetBool("FALSE_BOOL")
	assert.NoError(t, err)
	assert.False(t, boolVal)

	// Test zero duration
	manager.Set("ZERO_DURATION", "0s")
	duration, err := manager.GetDuration("ZERO_DURATION")
	assert.NoError(t, err)
	assert.Equal(t, time.Duration(0), duration)

	_ = os.Unsetenv("EMPTY_STRING")
	_ = os.Unsetenv("ZERO_INT")
	_ = os.Unsetenv("FALSE_BOOL")
	_ = os.Unsetenv("ZERO_DURATION")
}
