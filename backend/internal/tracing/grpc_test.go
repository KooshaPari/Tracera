//go:build !integration

package tracing

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

type testContextKey string

func TestParseMethodName(t *testing.T) {
	tests := []struct {
		name           string
		fullMethod     string
		expectedSvc    string
		expectedMethod string
	}{
		{
			name:           "standard method",
			fullMethod:     "/package.Service/Method",
			expectedSvc:    "Service",
			expectedMethod: "Method",
		},
		{
			name:           "nested package",
			fullMethod:     "/com.example.Service/GetData",
			expectedSvc:    "Service",
			expectedMethod: "GetData",
		},
		{
			name:           "without leading slash",
			fullMethod:     "MyService/MyMethod",
			expectedSvc:    "MyService",
			expectedMethod: "MyMethod",
		},
		{
			name:           "invalid format",
			fullMethod:     "invalid",
			expectedSvc:    "unknown",
			expectedMethod: "unknown",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			svc, method := parseMethodName(tt.fullMethod)
			assert.Equal(t, tt.expectedSvc, svc)
			assert.Equal(t, tt.expectedMethod, method)
		})
	}
}

func TestUnaryServerInterceptor(t *testing.T) {
	interceptor := UnaryServerInterceptor()
	require.NotNil(t, interceptor)

	ctx := context.Background()
	info := &grpc.UnaryServerInfo{
		FullMethod: "/test.Service/TestMethod",
	}

	t.Run("success case", func(t *testing.T) {
		handler := func(ctx context.Context, req interface{}) (interface{}, error) {
			return "response", nil
		}

		resp, err := interceptor(ctx, nil, info, handler)
		require.NoError(t, err)
		assert.Equal(t, "response", resp)
	})

	t.Run("error case", func(t *testing.T) {
		handler := func(ctx context.Context, req interface{}) (interface{}, error) {
			return nil, status.Error(codes.Internal, "test error")
		}

		resp, err := interceptor(ctx, nil, info, handler)
		require.Error(t, err)
		assert.Nil(t, resp)
	})

	t.Run("with metadata", func(t *testing.T) {
		md := metadata.Pairs(
			"user-id", "user123",
			"project-id", "proj456",
			"x-trace-id", "trace789",
		)
		ctx = metadata.NewIncomingContext(context.Background(), md)

		handler := func(ctx context.Context, req interface{}) (interface{}, error) {
			return "response", nil
		}

		resp, err := interceptor(ctx, nil, info, handler)
		require.NoError(t, err)
		assert.Equal(t, "response", resp)
	})
}

func TestStreamServerInterceptor(t *testing.T) {
	interceptor := StreamServerInterceptor()
	require.NotNil(t, interceptor)
}

func TestUnaryClientInterceptor(t *testing.T) {
	interceptor := UnaryClientInterceptor()
	require.NotNil(t, interceptor)
}

func TestStreamClientInterceptor(t *testing.T) {
	interceptor := StreamClientInterceptor()
	require.NotNil(t, interceptor)
}

func TestGRPCSpan(t *testing.T) {
	ctx := context.Background()
	newCtx, span := GRPCSpan(ctx, "TestService", "TestMethod")

	require.NotNil(t, span)
	require.NotNil(t, newCtx)

	defer span.End()

	// Span should not be nil (IsRecording may be false without actual tracer provider)
	assert.NotNil(t, span)
}

func TestWrappedServerStream(t *testing.T) {
	// Create a mock ServerStream
	mockStream := &testServerStream{
		ctx: context.Background(),
	}

	wrapped := &wrappedServerStream{
		ServerStream: mockStream,
		ctx:          context.WithValue(context.Background(), testContextKey("key"), "value"),
	}

	// Check that context is properly wrapped
	assert.Equal(t, "value", wrapped.Context().Value(testContextKey("key")))
}

// Mock ServerStream for testing
type testServerStream struct {
	grpc.ServerStream
	ctx context.Context
}

func (t *testServerStream) Context() context.Context {
	return t.ctx
}
