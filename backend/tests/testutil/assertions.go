package testutil

import (
	"encoding/json"
	"fmt"
	"reflect"
	"testing"
	"time"

	"github.com/nats-io/nats.go"
)

// AssertJSONResponse compares expected and actual JSON responses.
// This function handles JSON marshaling and provides detailed diff output on failure.
//
// Example:
//
//	expected := map[string]interface{}{"status": "success", "count": 5}
//	actual := map[string]interface{}{"status": "success", "count": 5}
//	AssertJSONResponse(t, expected, actual)
func AssertJSONResponse(t *testing.T, expected, actual interface{}) {
	t.Helper()

	expectedJSON, err := json.MarshalIndent(expected, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal expected JSON: %v", err)
	}

	actualJSON, err := json.MarshalIndent(actual, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal actual JSON: %v", err)
	}

	var expectedMap, actualMap interface{}
	if err := json.Unmarshal(expectedJSON, &expectedMap); err != nil {
		t.Fatalf("failed to unmarshal expected JSON: %v", err)
	}
	if err := json.Unmarshal(actualJSON, &actualMap); err != nil {
		t.Fatalf("failed to unmarshal actual JSON: %v", err)
	}

	if !reflect.DeepEqual(expectedMap, actualMap) {
		t.Errorf("JSON responses do not match\nExpected:\n%s\n\nActual:\n%s", expectedJSON, actualJSON)
	}
}

// AssertStatusCode verifies that the actual HTTP status code matches the expected one.
//
// Example:
//
//	AssertStatusCode(t, http.StatusOK, response.StatusCode)
func AssertStatusCode(t *testing.T, expected, actual int) {
	t.Helper()

	if expected != actual {
		t.Errorf("status code mismatch: expected %d, got %d", expected, actual)
	}
}

// AssertCacheHit verifies that a cache hit occurred based on cache statistics.
// This is useful for testing Redis caching behavior.
//
// Example:
//
//	stats := map[string]int{"hits": 1, "misses": 0}
//	AssertCacheHit(t, stats)
func AssertCacheHit(t *testing.T, cacheStats map[string]int) {
	t.Helper()

	hits, ok := cacheStats["hits"]
	if !ok {
		t.Error("cache stats missing 'hits' key")
		return
	}

	if hits == 0 {
		t.Error("expected cache hit, but got cache miss")
	}
}

// AssertCacheMiss verifies that a cache miss occurred based on cache statistics.
//
// Example:
//
//	stats := map[string]int{"hits": 0, "misses": 1}
//	AssertCacheMiss(t, stats)
func AssertCacheMiss(t *testing.T, cacheStats map[string]int) {
	t.Helper()

	misses, ok := cacheStats["misses"]
	if !ok {
		t.Error("cache stats missing 'misses' key")
		return
	}

	if misses == 0 {
		t.Error("expected cache miss, but got cache hit")
	}
}

// AssertEventPublished verifies that an event was published to NATS.
// This function subscribes to the topic and waits for the expected event.
//
// Example:
//
//	err := AssertEventPublished(t, "project.created", natsConn)
//	if err != nil {
//	    t.Fatalf("event not published: %v", err)
//	}
func AssertEventPublished(t *testing.T, eventType string, natsConn *nats.Conn) error {
	t.Helper()

	ch := make(chan *nats.Msg, 1)
	sub, err := natsConn.ChanSubscribe(eventType, ch)
	if err != nil {
		return fmt.Errorf("failed to subscribe to event: %w", err)
	}
	defer sub.Unsubscribe()

	select {
	case msg := <-ch:
		if msg == nil {
			return fmt.Errorf("received nil message for event type: %s", eventType)
		}
		return nil
	case <-time.After(5 * time.Second):
		return fmt.Errorf("timeout waiting for event: %s", eventType)
	}
}

// AssertEqual is a generic equality assertion helper.
//
// Example:
//
//	AssertEqual(t, "expected value", actualValue, "custom error message")
func AssertEqual(t *testing.T, expected, actual interface{}, msgAndArgs ...interface{}) {
	t.Helper()

	if !reflect.DeepEqual(expected, actual) {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("values not equal\nExpected: %v\nActual: %v\n%s", expected, actual, msg)
	}
}

// AssertNotEqual verifies that two values are not equal.
//
// Example:
//
//	AssertNotEqual(t, oldValue, newValue, "value should have changed")
func AssertNotEqual(t *testing.T, expected, actual interface{}, msgAndArgs ...interface{}) {
	t.Helper()

	if reflect.DeepEqual(expected, actual) {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("values should not be equal\nBoth values: %v\n%s", expected, msg)
	}
}

// AssertNil verifies that a value is nil.
//
// Example:
//
//	AssertNil(t, err, "expected no error")
func AssertNil(t *testing.T, value interface{}, msgAndArgs ...interface{}) {
	t.Helper()

	if value != nil && !reflect.ValueOf(value).IsNil() {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("expected nil value\nGot: %v\n%s", value, msg)
	}
}

// AssertNotNil verifies that a value is not nil.
//
// Example:
//
//	AssertNotNil(t, result, "expected result to be non-nil")
func AssertNotNil(t *testing.T, value interface{}, msgAndArgs ...interface{}) {
	t.Helper()

	if value == nil || (reflect.ValueOf(value).Kind() == reflect.Ptr && reflect.ValueOf(value).IsNil()) {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("expected non-nil value\n%s", msg)
	}
}

// AssertContains verifies that a string contains a substring.
//
// Example:
//
//	AssertContains(t, "hello world", "world", "should contain substring")
func AssertContains(t *testing.T, str, substr string, msgAndArgs ...interface{}) {
	t.Helper()

	if !contains(str, substr) {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("string does not contain substring\nString: %s\nSubstring: %s\n%s", str, substr, msg)
	}
}

// AssertNoError verifies that an error is nil.
//
// Example:
//
//	AssertNoError(t, err, "operation should succeed")
func AssertNoError(t *testing.T, err error, msgAndArgs ...interface{}) {
	t.Helper()

	if err != nil {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("expected no error, got: %v\n%s", err, msg)
	}
}

// AssertError verifies that an error occurred.
//
// Example:
//
//	AssertError(t, err, "expected operation to fail")
func AssertError(t *testing.T, err error, msgAndArgs ...interface{}) {
	t.Helper()

	if err == nil {
		msg := ""
		if len(msgAndArgs) > 0 {
			msg = fmt.Sprintf(msgAndArgs[0].(string), msgAndArgs[1:]...)
		}
		t.Errorf("expected error, got nil\n%s", msg)
	}
}

// contains is a helper function to check if a string contains a substring.
func contains(str, substr string) bool {
	return len(str) >= len(substr) && (str == substr || len(substr) == 0 || findSubstring(str, substr))
}

// findSubstring searches for a substring in a string.
func findSubstring(str, substr string) bool {
	for i := 0; i <= len(str)-len(substr); i++ {
		if str[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
