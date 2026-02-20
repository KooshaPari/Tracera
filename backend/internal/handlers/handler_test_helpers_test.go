package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type listValidationTest struct {
	name           string
	queryString    string
	expectedStatus int
	shouldContain  string
}

func runListValidationTests(
	t *testing.T,
	tests []listValidationTest,
	path string,
	call func(handler interface{}, c echo.Context) error,
	newHandler func(t *testing.T, mock pgxmock.PgxPoolIface) interface{},
) {
	t.Helper()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := newHandler(t, mock)
			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, path+tt.queryString, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			err = call(handler, c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed50, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed50, tt.shouldContain)
			}
		})
	}
}
