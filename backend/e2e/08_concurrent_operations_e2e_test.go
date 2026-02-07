//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Journey 8: Concurrent Operations - Conflict Resolution (30+ tests)

func TestE2E_Concurrent_MultipleUpdates(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Concurrent Project")
	item := createTestItem(t, srv, projectID, "Concurrent Item", "requirement")

	var wg sync.WaitGroup
	results := make([]int, 10)

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			payload := map[string]interface{}{
				"title": "Update " + string(rune(idx)),
			}
			body, _ := json.Marshal(payload)

			req, _ := http.NewRequest("PATCH", srv.URL+"/api/items/"+item, bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")

			resp, err := http.DefaultClient.Do(req)
			if err == nil {
				results[idx] = resp.StatusCode
				resp.Body.Close()
			}
		}(i)
	}

	wg.Wait()

	successCount := 0
	for _, status := range results {
		if status == http.StatusOK {
			successCount++
		}
	}

	assert.GreaterOrEqual(t, successCount, 8)
}
