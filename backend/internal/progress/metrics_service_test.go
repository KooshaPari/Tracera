//go:build !integration

package progress

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewMetricsService(t *testing.T) {
	svc := NewMetricsService(nil)
	require.NotNil(t, svc)
}

func TestGroupedCountQuery(t *testing.T) {
	tests := []struct {
		field   string
		wantErr bool
		wantSQL string
	}{
		{"status", false, "SELECT status"},
		{"priority", false, "SELECT priority"},
		{"type", false, "SELECT type"},
		{"invalid", true, ""},
	}

	for _, tt := range tests {
		t.Run(tt.field, func(t *testing.T) {
			query, err := groupedCountQuery(tt.field)
			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "unsupported group field")
			} else {
				require.NoError(t, err)
				assert.Contains(t, query, tt.wantSQL)
				assert.Contains(t, query, "COUNT(*)")
				assert.Contains(t, query, "GROUP BY")
			}
		})
	}
}

func TestNewProjectMetrics(t *testing.T) {
	m := newProjectMetrics()
	require.NotNil(t, m)
	assert.NotNil(t, m.ByStatus)
	assert.NotNil(t, m.ByPriority)
	assert.NotNil(t, m.ByType)
	assert.NotNil(t, m.ByLifecycle)
	assert.Equal(t, 0, m.TotalItems)
}

func TestCloseRows_NilDoesNotPanic(t *testing.T) {
	assert.NotPanics(t, func() {
		closeRows(nil)
	})
}
