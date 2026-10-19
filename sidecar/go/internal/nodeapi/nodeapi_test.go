package nodeapi

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestClientEnrollUsesFleetPath(t *testing.T) {
	var got string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got = r.URL.Path
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(EnrollResponse{Accepted: true, Generation: 7})
	}))
	defer srv.Close()

	c := NewClient(srv.URL, "tok", 0)
	resp, err := c.Enroll(context.Background(), EnrollRequest{NodeID: "n1"})
	if err != nil {
		t.Fatalf("enroll: %v", err)
	}
	if got != "/fleet/enroll" {
		t.Fatalf("expected /fleet/enroll, got %s", got)
	}
	if resp.Generation != 7 {
		t.Fatalf("expected generation=7, got %d", resp.Generation)
	}
}

func TestFetchDesiredEncodesNodeID(t *testing.T) {
	var got string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got = r.URL.RawQuery
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(DesiredState{Generation: 1})
	}))
	defer srv.Close()

	c := NewClient(srv.URL, "tok", 0)
	if _, err := c.FetchDesired(context.Background(), "n with space"); err != nil {
		t.Fatalf("fetch: %v", err)
	}
	if got != "node_id=n+with+space" {
		t.Fatalf("expected escaped query, got %s", got)
	}
}

func TestReportUsesFleetPath(t *testing.T) {
	var got string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got = r.URL.Path
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	c := NewClient(srv.URL, "tok", 0)
	if err := c.Report(context.Background(), Status{NodeID: "n1", Generation: 1}); err != nil {
		t.Fatalf("report: %v", err)
	}
	if got != "/fleet/report" {
		t.Fatalf("expected /fleet/report, got %s", got)
	}
}
