package tracing

import (
	"context"
	"fmt"
	"strings"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

const (
	grpcInstrumentationName   = "tracertm-grpc"
	grpcStatusCodeAttr        = "grpc.status_code"
	grpcMethodAttr            = "grpc.method"
	grpcServiceAttr           = "grpc.service"
	grpcRequestSizeAttr       = "grpc.request_size"
	grpcResponseSizeAttr      = "grpc.response_size"
	grpcClientInterceptorName = "grpc.client"
	grpcServerInterceptorName = "grpc.server"
)

var grpcTracer = otel.Tracer(grpcInstrumentationName)

// UnaryServerInterceptor returns a gRPC unary server interceptor that instruments
// gRPC unary RPC calls with OpenTelemetry spans
func UnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		// Extract service and method from full method name (e.g., "/package.Service/Method")
		service, method := parseMethodName(info.FullMethod)

		// Create span
		spanName := fmt.Sprintf("%s/%s", service, method)
		ctx, span := grpcTracer.Start(ctx, spanName, trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		// Set gRPC-specific attributes
		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, method),
			attribute.String(grpcInstrumentationName, "true"),
		)

		// Extract metadata (for debugging and propagation)
		if md, ok := metadata.FromIncomingContext(ctx); ok {
			// Extract trace context from metadata (if present)
			traceIDs := md.Get("x-trace-id")
			if len(traceIDs) > 0 {
				span.SetAttributes(attribute.String("trace.id", traceIDs[0]))
			}

			// Extract user info if present
			userIDs := md.Get("user-id")
			if len(userIDs) > 0 {
				span.SetAttributes(attribute.String("user.id", userIDs[0]))
			}

			// Extract project info if present
			projectIDs := md.Get("project-id")
			if len(projectIDs) > 0 {
				span.SetAttributes(attribute.String("project.id", projectIDs[0]))
			}
		}

		// Call the actual handler
		resp, err := handler(ctx, req)

		// Record response status
		if err != nil {
			// Extract gRPC status code
			st, ok := status.FromError(err)
			if ok {
				span.SetAttributes(
					attribute.String(grpcStatusCodeAttr, st.Code().String()),
					attribute.String("error.message", st.Message()),
				)
			}
			span.RecordError(err)
			span.SetStatus(codes.Error, "gRPC call failed")
		} else {
			span.SetStatus(codes.Ok, "")
			span.SetAttributes(
				attribute.String(grpcStatusCodeAttr, "OK"),
			)
		}

		return resp, err
	}
}

// StreamServerInterceptor returns a gRPC stream server interceptor that instruments
// gRPC streaming RPC calls with OpenTelemetry spans
func StreamServerInterceptor() grpc.StreamServerInterceptor {
	return func(
		srv interface{},
		ss grpc.ServerStream,
		info *grpc.StreamServerInfo,
		handler grpc.StreamHandler,
	) error {
		// Extract service and method from full method name
		service, method := parseMethodName(info.FullMethod)

		// Create span
		spanName := fmt.Sprintf("%s/%s (stream)", service, method)
		ctx, span := grpcTracer.Start(ss.Context(), spanName, trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		// Set gRPC-specific attributes
		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, method),
			attribute.String("grpc.stream_type", func() string {
				if info.IsClientStream && info.IsServerStream {
					return "bidi_stream"
				} else if info.IsClientStream {
					return "client_stream"
				} else if info.IsServerStream {
					return "server_stream"
				}
				return "unknown"
			}()),
		)

		// Extract metadata
		if md, ok := metadata.FromIncomingContext(ctx); ok {
			traceIDs := md.Get("x-trace-id")
			if len(traceIDs) > 0 {
				span.SetAttributes(attribute.String("trace.id", traceIDs[0]))
			}

			userIDs := md.Get("user-id")
			if len(userIDs) > 0 {
				span.SetAttributes(attribute.String("user.id", userIDs[0]))
			}
		}

		// Wrap the stream with a new context
		wrappedStream := &wrappedServerStream{
			ServerStream: ss,
			ctx:          ctx,
		}

		// Call the actual handler
		err := handler(srv, wrappedStream)

		// Record error status
		if err != nil {
			st, ok := status.FromError(err)
			if ok {
				span.SetAttributes(
					attribute.String(grpcStatusCodeAttr, st.Code().String()),
					attribute.String("error.message", st.Message()),
				)
			}
			span.RecordError(err)
			span.SetStatus(codes.Error, "gRPC stream failed")
		} else {
			span.SetStatus(codes.Ok, "")
			span.SetAttributes(
				attribute.String(grpcStatusCodeAttr, "OK"),
			)
		}

		return err
	}
}

// UnaryClientInterceptor returns a gRPC unary client interceptor for instrumenting
// outgoing gRPC calls (useful for testing and inter-service communication)
func UnaryClientInterceptor() grpc.UnaryClientInterceptor {
	return func(
		ctx context.Context,
		method string,
		req, reply interface{},
		cc *grpc.ClientConn,
		invoker grpc.UnaryInvoker,
		opts ...grpc.CallOption,
	) error {
		service, methodName := parseMethodName(method)
		spanName := fmt.Sprintf("%s/%s", service, methodName)

		ctx, span := grpcTracer.Start(ctx, spanName,
			trace.WithSpanKind(trace.SpanKindClient),
		)
		defer span.End()

		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, methodName),
			attribute.String("rpc.system", "grpc"),
		)

		// Invoke the actual call
		err := invoker(ctx, method, req, reply, cc, opts...)

		if err != nil {
			st, ok := status.FromError(err)
			if ok {
				span.SetAttributes(
					attribute.String(grpcStatusCodeAttr, st.Code().String()),
				)
			}
			span.RecordError(err)
			span.SetStatus(codes.Error, "gRPC call failed")
		} else {
			span.SetStatus(codes.Ok, "")
		}

		return err
	}
}

// StreamClientInterceptor returns a gRPC stream client interceptor for instrumenting
// outgoing gRPC streaming calls
func StreamClientInterceptor() grpc.StreamClientInterceptor {
	return func(
		ctx context.Context,
		desc *grpc.StreamDesc,
		cc *grpc.ClientConn,
		method string,
		streamer grpc.Streamer,
		opts ...grpc.CallOption,
	) (grpc.ClientStream, error) {
		service, methodName := parseMethodName(method)
		spanName := fmt.Sprintf("%s/%s (stream)", service, methodName)

		ctx, span := grpcTracer.Start(ctx, spanName,
			trace.WithSpanKind(trace.SpanKindClient),
		)
		defer span.End()

		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, methodName),
			attribute.String("rpc.system", "grpc"),
			attribute.String("grpc.stream_type", func() string {
				if desc.ClientStreams && desc.ServerStreams {
					return "bidi_stream"
				} else if desc.ClientStreams {
					return "client_stream"
				} else if desc.ServerStreams {
					return "server_stream"
				}
				return "unknown"
			}()),
		)

		cs, err := streamer(ctx, desc, cc, method, opts...)
		if err != nil {
			span.RecordError(err)
			span.SetStatus(codes.Error, "failed to create stream")
			return cs, err
		}

		return cs, nil
	}
}

// wrappedServerStream wraps a grpc.ServerStream and injects context
type wrappedServerStream struct {
	grpc.ServerStream
	ctx context.Context
}

// Context returns the wrapped context
func (w *wrappedServerStream) Context() context.Context {
	return w.ctx
}

// parseMethodName parses a gRPC method name into service and method components
// e.g., "/package.Service/Method" -> ("Service", "Method")
func parseMethodName(fullMethod string) (string, string) {
	// Remove leading slash
	fullMethod = strings.TrimPrefix(fullMethod, "/")

	// Split by the last slash
	parts := strings.Split(fullMethod, "/")
	if len(parts) != 2 {
		return "unknown", "unknown"
	}

	// Extract service name (everything after the last dot)
	serviceParts := strings.Split(parts[0], ".")
	service := serviceParts[len(serviceParts)-1]

	return service, parts[1]
}

// GRPCSpan creates a span for gRPC operations (for manual instrumentation)
func GRPCSpan(ctx context.Context, service string, method string) (context.Context, trace.Span) {
	spanName := fmt.Sprintf("%s/%s", service, method)
	ctx, span := grpcTracer.Start(ctx, spanName, trace.WithSpanKind(trace.SpanKindClient))

	SetAttributes(span,
		attribute.String(grpcServiceAttr, service),
		attribute.String(grpcMethodAttr, method),
		attribute.String("rpc.system", "grpc"),
	)

	return ctx, span
}
