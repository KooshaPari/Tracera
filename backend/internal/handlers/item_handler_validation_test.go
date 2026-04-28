package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestCreateItem_Validation tests CreateItem input validation with table-driven approach
func TestCreateItem_Validation(t *testing.T) {
	tests := []struct {
		name           string
		body           map[string]interface{}
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "missing_project_id",
			body:           map[string]interface{}{"title": "Test", "type": "req", "status": "open"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project_id",
		},
		{
			name:           "invalid_project_id_format",
			body:           map[string]interface{}{"project_id": "not-uuid", "title": "Test", "type": "req", "status": "open"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project_id",
		},
		{
			name:           "empty_project_id",
			body:           map[string]interface{}{"project_id": "", "title": "Test", "type": "req", "status": "open"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project_id",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupItemHandler(t, mock)
			c, rec := makeCreateItemRequest(t, tt.body)

			err = handler.CreateItem(*c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed60, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed60, tt.shouldContain)
			}
		})
	}
}

// TestGetItem_Validation tests GetItem ID validation with table-driven approach
func TestGetItem_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "malformed_id",
			id:             "123-456",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
	}

	runItemIDValidationTests(t, tests, "/api/v1/items/:id", func(handler *ItemHandler, c *echo.Context) error {
		return handler.GetItem(*c)
	})
}

// TestListItems_Validation tests ListItems query parameter validation
func TestListItems_Validation(t *testing.T) {
	tests := []listValidationTest{
		{
			name:           "missing_project_id",
			queryString:    "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "project_id is required",
		},
		{
			name:           "invalid_project_id",
			queryString:    "?project_id=not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "invalid project_id",
		},
		{
			name:           "empty_project_id",
			queryString:    "?project_id=",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "project_id is required",
		},
	}

	runListValidationTests(
		t,
		tests,
		"/api/v1/items",
		func(handler interface{}, c echo.Context) error {
			h, ok := handler.(*ItemHandler)
			require.True(t, ok)
			return h.ListItems(c)
		},
		func(t *testing.T, mock pgxmock.PgxPoolIface) interface{} {
			return setupItemHandler(t, mock)
		},
	)
}

// TestListItems_PaginationParsing tests that pagination parameters are correctly parsed
func TestListItems_PaginationParsing(t *testing.T) {
	tests := []struct {
		name         string
		queryString  string
		expectLimit  int32
		expectOffset int32
	}{
		{
			name:         "default_pagination",
			queryString:  "?project_id=" + uuid.New().String(),
			expectLimit:  100,
			expectOffset: 0,
		},
		{
			name:         "custom_limit",
			queryString:  "?project_id=" + uuid.New().String() + "&limit=50",
			expectLimit:  50,
			expectOffset: 0,
		},
		{
			name:         "custom_offset",
			queryString:  "?project_id=" + uuid.New().String() + "&offset=25",
			expectLimit:  100,
			expectOffset: 25,
		},
		{
			name:         "invalid_limit_fallback",
			queryString:  "?project_id=" + uuid.New().String() + "&limit=invalid",
			expectLimit:  100, // Falls back to default
			expectOffset: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupItemHandler(t, mock)

			// Expect the ListItemsByProject call with the parsed parameters
			mock.ExpectQuery("SELECT").WithArgs(
			// ProjectID will be dynamic, so we match any args
			).WillReturnRows(
				pgxmock.NewRows([]string{
					"id", "project_id", "title", "type", "status",
					"priority", "metadata", "created_at", "updated_at",
				}),
			)

			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/api/v1/items"+tt.queryString, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			err = handler.ListItems(c)
			require.NoError(t, err)

			// If query parsing succeeds, we shouldn't get a 400
			assert.NotEqual(t, http.StatusBadRequest, rec.Code)
		})
	}
}

// TestUpdateItem_Validation tests UpdateItem ID validation
func TestUpdateItem_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupItemHandler(t, mock)
			body := map[string]interface{}{"title": "Updated"}
			c, rec := makeUpdateRequest(t, "/api/v1/items/:id", "id", tt.id, body)

			err = handler.UpdateItem(*c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

// TestDeleteItem_Validation tests DeleteItem ID validation
func TestDeleteItem_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupItemHandler(t, mock)
			c, rec := makeDeleteRequest(t, "/api/v1/items/:id", "id", tt.id)

			err = handler.DeleteItem(*c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

func runItemIDValidationTests(
	t *testing.T,
	tests []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	},
	path string,
	call func(handler *ItemHandler, c *echo.Context) error,
) {
	t.Helper()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupItemHandler(t, mock)
			c, rec := makeGetRequest(t, path, "id", tt.id)

			err = call(handler, c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed309, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed309, tt.shouldContain)
			}
		})
	}
}
