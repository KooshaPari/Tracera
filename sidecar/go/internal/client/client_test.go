package client

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestDispatchAndReadinessContract(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/readyz" {
			if r.Method != http.MethodGet || r.Header.Get("X-Request-ID") != "req-1" {
				t.Errorf("readiness request = %s %s request-id=%q", r.Method, r.URL.Path, r.Header.Get("X-Request-ID"))
			}
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"status":"ready"}`))
			return
		}
		if r.Method != http.MethodPost || r.Header.Get("Idempotency-Key") != "idem-1" || r.Header.Get("Content-Type") != "application/json" {
			t.Errorf("dispatch headers/method invalid: %s %v", r.Method, r.Header)
		}
		var payload map[string]string
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil || payload["job"] != "sync" {
			t.Errorf("payload = %#v, err=%v", payload, err)
		}
		_, _ = w.Write([]byte(`{"accepted":true}`))
	}))
	defer server.Close()
	c, err := New(server.URL, time.Second)
	if err != nil {
		t.Fatal(err)
	}
	if _, err = c.Readiness(context.Background(), "req-1"); err != nil {
		t.Fatal(err)
	}
	resp, err := c.Dispatch(context.Background(), http.MethodPost, "/dispatch", map[string]string{"job": "sync"}, "req-2", "idem-1")
	if err != nil || resp.StatusCode != http.StatusOK {
		t.Fatalf("dispatch = %#v, err=%v", resp, err)
	}
}

func TestDispatchReturnsHTTPErrorAndValidatesPath(t *testing.T) {
	server := httptest.NewServer(http.NotFoundHandler())
	defer server.Close()
	c, _ := New(server.URL, time.Second)
	resp, err := c.Dispatch(context.Background(), http.MethodGet, "/missing", nil, "", "")
	var httpErr *HTTPError
	if !errors.As(err, &httpErr) || httpErr.StatusCode != http.StatusNotFound || resp.StatusCode != http.StatusNotFound {
		t.Fatalf("expected bounded HTTP error, resp=%#v err=%v", resp, err)
	}
	if _, err = c.Dispatch(context.Background(), http.MethodGet, "missing", nil, "", ""); err == nil {
		t.Fatal("expected absolute path validation error")
	}
}

func TestNewRejectsInvalidConfiguration(t *testing.T) {
	if _, err := New("", time.Second); err == nil {
		t.Fatal("expected missing base URL error")
	}
	if _, err := New("http://example.test", 0); err == nil {
		t.Fatal("expected non-positive timeout error")
	}
}
