package handlers

import (
	"bufio"
	"context"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Mock repositories and services
type MockItemRepository struct {
	mock.Mock
}

func (m *MockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}

func TestStreamHandler_Creation(t *testing.T) {
	mockRepo := new(MockItemRepository)
	handler := NewStreamHandler(mockRepo)

	assert.NotNil(t, handler)
	assert.NotNil(t, handler.itemRepo)
}

func TestStreamHandler_writeNDJSONLine(t *testing.T) {
	mockRepo := new(MockItemRepository)
	handler := NewStreamHandler(mockRepo)

	tests := []struct {
		name     string
		data     interface{}
		expected string
	}{
		{
			name:     "simple object",
			data:     map[string]string{"key": "value"},
			expected: `{"key":"value"}` + "\n",
		},
		{
			name:     "nested object",
			data:     map[string]interface{}{"outer": map[string]string{"inner": "value"}},
			expected: `{"outer":{"inner":"value"}}` + "\n",
		},
		{
			name:     "array",
			data:     []string{"a", "b", "c"},
			expected: `["a","b","c"]` + "\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var buf strings.Builder
			writer := bufio.NewWriter(&buf)

			err := handler.writeNDJSONLine(writer, tt.data)
			require.NoError(t, err)

			err = writer.Flush()
			require.NoError(t, err)
			assert.Equal(t, tt.expected, buf.String())
		})
	}
}
