package temporal

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"
)

func TestNewZapAdapter(t *testing.T) {
	logger := zap.NewNop()
	adapter := NewZapAdapter(logger)

	assert.NotNil(t, adapter)
	assert.NotNil(t, adapter.logger)

	// Test logging methods (should not panic)
	adapter.Debug("test debug", "key", "value")
	adapter.Info("test info", "key", "value")
	adapter.Warn("test warn", "key", "value")
	adapter.Error("test error", "key", "value")
}

func TestToZapFields(t *testing.T) {
	tests := []struct {
		name     string
		keyvals  []interface{}
		expected int
	}{
		{
			name:     "empty",
			keyvals:  []interface{}{},
			expected: 0,
		},
		{
			name:     "single pair",
			keyvals:  []interface{}{"key1", "value1"},
			expected: 1,
		},
		{
			name:     "multiple pairs",
			keyvals:  []interface{}{"key1", "value1", "key2", 123},
			expected: 2,
		},
		{
			name:     "odd number of elements (last ignored)",
			keyvals:  []interface{}{"key1", "value1", "key2"},
			expected: 1,
		},
		{
			name:     "non-string key (skipped)",
			keyvals:  []interface{}{123, "value1", "key2", "value2"},
			expected: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			fields := toZapFields(tt.keyvals)
			assert.Len(t, fields, tt.expected)
		})
	}
}

func TestNowUnixMilli(t *testing.T) {
	// Test that nowUnixMilli returns a reasonable timestamp
	timestamp := nowUnixMilli()

	// Should be a positive number (milliseconds since epoch)
	assert.Positive(t, timestamp)

	// Should be in reasonable range (after 2020, before 2100)
	minTimestamp := int64(1577836800000) // 2020-01-01
	maxTimestamp := int64(4102444800000) // 2100-01-01
	assert.Greater(t, timestamp, minTimestamp)
	assert.Less(t, timestamp, maxTimestamp)
}
