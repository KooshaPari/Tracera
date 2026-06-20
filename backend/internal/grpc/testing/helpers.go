// Package testing provides utilities for testing gRPC services in Go
package testing

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"testing"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/connectivity"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"
)

const (
	testBufConnKiB             = 1024
	testBufConnMiB             = 1024
	testBufConnSizeBytes       = testBufConnKiB * testBufConnMiB
	microsecondsPerMillisecond = 1000.0
)

// TestServer wraps a gRPC server for testing
type TestServer struct {
	Server   *grpc.Server
	Listener *bufconn.Listener
	t        *testing.T
}

// NewTestServer creates a new test gRPC server
func NewTestServer(t *testing.T, opts ...grpc.ServerOption) *TestServer {
	// Create a buffer connection with 1MB buffer
	listener := bufconn.Listen(testBufConnSizeBytes)

	server := grpc.NewServer(opts...)

	return &TestServer{
		Server:   server,
		Listener: listener,
		t:        t,
	}
}

// Start starts the test server in the background
func (ts *TestServer) Start() {
	go func() {
		if err := ts.Server.Serve(ts.Listener); err != nil {
			ts.t.Logf("Server exited with error: %v", err)
		}
	}()
}

// Stop gracefully stops the test server
func (ts *TestServer) Stop() {
	ts.Server.GracefulStop()
	if err := ts.Listener.Close(); err != nil {
		ts.t.Logf("Failed to close listener: %v", err)
	}
}

// Dialer returns a dialer function for connecting to the test server
func (ts *TestServer) Dialer() func(context.Context, string) (net.Conn, error) {
	return func(context.Context, string) (net.Conn, error) {
		return ts.Listener.Dial()
	}
}

// NewClient creates a client connection to the test server
func (ts *TestServer) NewClient(_ context.Context, opts ...grpc.DialOption) (*grpc.ClientConn, error) {
	// Add buffer dialer to options
	opts = append(opts,
		grpc.WithContextDialer(ts.Dialer()),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)

	return grpc.NewClient("bufnet", opts...)
}

// RequestLogger logs gRPC requests and responses
type RequestLogger struct {
	serviceName string
	verbose     bool
	requests    []LogEntry
	responses   []LogEntry
}

// LogEntry represents a logged request or response
type LogEntry struct {
	Timestamp  time.Time
	Method     string
	Message    interface{}
	DurationMs float64
	Error      error
}

// NewRequestLogger creates a new request logger
func NewRequestLogger(serviceName string, verbose bool) *RequestLogger {
	return &RequestLogger{
		serviceName: serviceName,
		verbose:     verbose,
		requests:    make([]LogEntry, 0),
		responses:   make([]LogEntry, 0),
	}
}

// LogRequest logs a gRPC request
func (rl *RequestLogger) LogRequest(method string, msg interface{}) {
	entry := LogEntry{
		Timestamp: time.Now(),
		Method:    method,
		Message:   msg,
	}
	rl.requests = append(rl.requests, entry)

	if rl.verbose {
		slog.Info("📤 .", "name", rl.serviceName, "detail", method)
		slog.Info("Request", "detail", msg)
	}
}

// LogResponse logs a gRPC response
func (rl *RequestLogger) LogResponse(method string, msg interface{}, duration time.Duration) {
	durationMs := float64(duration.Microseconds()) / microsecondsPerMillisecond
	entry := LogEntry{
		Timestamp:  time.Now(),
		Method:     method,
		Message:    msg,
		DurationMs: durationMs,
	}
	rl.responses = append(rl.responses, entry)

	if rl.verbose {
		slog.Info("📥 . ( ms)", "name", rl.serviceName, "detail", method, "detail", durationMs)
		slog.Info("Response", "detail", msg)
	}
}

// LogError logs a gRPC error
func (rl *RequestLogger) LogError(method string, err error, duration time.Duration) {
	durationMs := float64(duration.Microseconds()) / microsecondsPerMillisecond
	entry := LogEntry{
		Timestamp:  time.Now(),
		Method:     method,
		Error:      err,
		DurationMs: durationMs,
	}
	rl.responses = append(rl.responses, entry)

	if rl.verbose {
		slog.Error("❌ . failed ( ms)", "name", rl.serviceName, "detail", method, "error", durationMs)
		slog.Error("Error", "error", err)
	}
}

// GetStats returns statistics about logged requests
func (rl *RequestLogger) GetStats() map[string]interface{} {
	totalRequests := len(rl.requests)
	successful := 0
	failed := 0
	var totalDuration float64

	for _, resp := range rl.responses {
		if resp.Error == nil {
			successful++
		} else {
			failed++
		}
		totalDuration += resp.DurationMs
	}

	avgDuration := 0.0
	if len(rl.responses) > 0 {
		avgDuration = totalDuration / float64(len(rl.responses))
	}

	successRate := 0.0
	if totalRequests > 0 {
		successRate = float64(successful) / float64(totalRequests)
	}

	return map[string]interface{}{
		"total_requests": totalRequests,
		"successful":     successful,
		"failed":         failed,
		"success_rate":   successRate,
		"avg_duration":   avgDuration,
	}
}

// Clear clears all logged entries
func (rl *RequestLogger) Clear() {
	rl.requests = make([]LogEntry, 0)
	rl.responses = make([]LogEntry, 0)
}

// AssertGRPCError asserts that a gRPC error has the expected code and message
func AssertGRPCError(t *testing.T, err error, expectedCode codes.Code, expectedMessage string) {
	t.Helper()

	if err == nil {
		t.Fatal("Expected error but got nil")
	}

	st, ok := status.FromError(err)
	if !ok {
		t.Fatalf("Expected gRPC status error, got: %v", err)
	}

	if st.Code() != expectedCode {
		t.Errorf("Expected status code %v, got %v", expectedCode, st.Code())
	}

	if expectedMessage != "" {
		if st.Message() != expectedMessage && !contains(st.Message(), expectedMessage) {
			t.Errorf("Expected message containing '%s', got '%s'", expectedMessage, st.Message())
		}
	}
}

// WaitForServer waits for a gRPC server to be ready
func WaitForServer(ctx context.Context, target string, timeout time.Duration) error {
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	conn, err := grpc.NewClient(
		target,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return fmt.Errorf("failed to connect to server: %w", err)
	}
	defer func() {
		if err := conn.Close(); err != nil {
			slog.Error("Failed to close gRPC connection", "error", err)
		}
	}()

	conn.Connect()
	for {
		state := conn.GetState()
		if state == connectivity.Ready {
			return nil
		}
		if !conn.WaitForStateChange(ctx, state) {
			if err := ctx.Err(); err != nil {
				return err
			}
			return errors.New("failed to connect to server")
		}
	}
}

// Helper function to check if string contains substring
func contains(s, substr string) bool {
	return len(s) >= len(substr) && s[0:len(substr)] == substr
}

// MockServicer provides common functionality for mock gRPC servicers
type MockServicer struct {
	Calls []CallRecord
}

// CallRecord represents a recorded method call
type CallRecord struct {
	Method    string
	Request   interface{}
	Timestamp time.Time
}

// RecordCall records a method call
func (servicer *MockServicer) RecordCall(method string, request interface{}) {
	servicer.Calls = append(servicer.Calls, CallRecord{
		Method:    method,
		Request:   request,
		Timestamp: time.Now(),
	})
}

// GetCallCount returns the number of calls (optionally filtered by method)
func (servicer *MockServicer) GetCallCount(method string) int {
	if method == "" {
		return len(servicer.Calls)
	}

	count := 0
	for _, call := range servicer.Calls {
		if call.Method == method {
			count++
		}
	}
	return count
}

// GetLastRequest returns the last request for a specific method
func (servicer *MockServicer) GetLastRequest(method string) interface{} {
	for i := len(servicer.Calls) - 1; i >= 0; i-- {
		if servicer.Calls[i].Method == method {
			return servicer.Calls[i].Request
		}
	}
	return nil
}

// ClearCalls clears all recorded calls
func (servicer *MockServicer) ClearCalls() {
	servicer.Calls = make([]CallRecord, 0)
}

/*
Example usage in tests:

package grpc_test

import (
	"context"
	"testing"
	"time"

	pb "github.com/yourorg/yourproject/pkg/proto"
	grpctest "github.com/yourorg/yourproject/internal/grpc/testing"
)

func TestGraphService_AnalyzeImpact(t *testing.T) {
	// Create test server
	ts := grpctest.NewTestServer(t)
	defer ts.Stop()

	// Register your service
	service := &YourGraphService{}
	pb.RegisterGraphServiceServer(ts.Server, service)

	// Start server
	ts.Start()

	// Create client
	ctx := context.Background()
	conn, err := ts.NewClient(ctx)
	if err != nil {
		t.Fatalf("Failed to create client: %v", err)
	}
	defer func() {
		if err := conn.Close(); err != nil {
			t.Logf("Failed to close connection: %v", err)
		}
	}()

	client := pb.NewGraphServiceClient(conn)

	// Create logger
	logger := grpctest.NewRequestLogger("GraphService", true)

	// Make request
	req := &pb.AnalyzeImpactRequest{
		ItemId:    "test-123",
		ProjectId: "proj-456",
		Direction: "both",
		MaxDepth:  2,
	}

	logger.LogRequest("AnalyzeImpact", req)
	start := time.Now()

	resp, err := client.AnalyzeImpact(ctx, req)

	duration := time.Since(start)
	if err != nil {
		logger.LogError("AnalyzeImpact", err, duration)
		t.Fatalf("AnalyzeImpact failed: %v", err)
	}
	logger.LogResponse("AnalyzeImpact", resp, duration)

	// Verify response
	if resp.TotalCount == 0 {
		t.Error("Expected non-zero impact count")
	}

	// Check stats
	stats := logger.GetStats()
	if stats["successful"].(int) != 1 {
		t.Errorf("Expected 1 successful call, got %d", stats["successful"])
	}
}

func TestGraphService_ErrorHandling(t *testing.T) {
	ts := grpctest.NewTestServer(t)
	defer ts.Stop()

	service := &YourGraphService{}
	pb.RegisterGraphServiceServer(ts.Server, service)
	ts.Start()

	ctx := context.Background()
	conn, err := ts.NewClient(ctx)
	if err != nil {
		t.Fatalf("Failed to create client: %v", err)
	}
	defer func() {
		if err := conn.Close(); err != nil {
			t.Logf("Failed to close connection: %v", err)
		}
	}()

	client := pb.NewGraphServiceClient(conn)

	// Test invalid request
	req := &pb.AnalyzeImpactRequest{
		ItemId: "", // Invalid empty ID
	}

	_, err = client.AnalyzeImpact(ctx, req)
	grpctest.AssertGRPCError(t, err, codes.InvalidArgument, "item_id")
}
*/
