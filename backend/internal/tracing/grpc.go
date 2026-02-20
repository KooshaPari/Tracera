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
	grpcStreamTypeUnknown     = "unknown"
)

func getGRPCTracer() trace.Tracer {
	return otel.Tracer(grpcInstrumentationName)
}

// annotateSpanFromMetadata extracts trace/user/project IDs from gRPC metadata and sets them on the span.
func annotateSpanFromMetadata(ctx context.Context, span trace.Span) {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return
	}
	if traceIDs := md.Get("x-trace-id"); len(traceIDs) > 0 {
		span.SetAttributes(attribute.String("trace.id", traceIDs[0]))
	}
	if userIDs := md.Get("user-id"); len(userIDs) > 0 {
		span.SetAttributes(attribute.String("user.id", userIDs[0]))
	}
	if projectIDs := md.Get("project-id"); len(projectIDs) > 0 {
		span.SetAttributes(attribute.String("project.id", projectIDs[0]))
	}
}

// recordGRPCResult sets span status and attributes based on the handler error.
func recordGRPCResult(span trace.Span, err error) {
	if err != nil {
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
		span.SetAttributes(attribute.String(grpcStatusCodeAttr, "OK"))
	}
}

// UnaryServerInterceptor returns a gRPC unary server interceptor that instruments
// gRPC unary RPC calls with OpenTelemetry spans
func UnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		service, method := parseMethodName(info.FullMethod)
		spanName := fmt.Sprintf("%s/%s", service, method)
		ctx, span := getGRPCTracer().Start(ctx, spanName, trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, method),
			attribute.String(grpcInstrumentationName, "true"),
		)
		annotateSpanFromMetadata(ctx, span)

		resp, err := handler(ctx, req)
		recordGRPCResult(span, err)

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
		service, method := parseMethodName(info.FullMethod)
		spanName := fmt.Sprintf("%s/%s (stream)", service, method)
		ctx, span := getGRPCTracer().Start(ss.Context(), spanName, trace.WithSpanKind(trace.SpanKindServer))
		defer span.End()

		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, method),
			attribute.String("grpc.stream_type", grpcStreamType(info)),
		)
		annotateSpanFromMetadata(ctx, span)

		wrappedStream := &wrappedServerStream{ServerStream: ss, ctx: ctx}
		err := handler(srv, wrappedStream)
		recordGRPCResult(span, err)

		return err
	}
}

// grpcStreamType returns the stream type string based on stream info flags.
func grpcStreamType(info *grpc.StreamServerInfo) string {
	switch {
	case info.IsClientStream && info.IsServerStream:
		return "bidi_stream"
	case info.IsClientStream:
		return "client_stream"
	case info.IsServerStream:
		return "server_stream"
	default:
		return grpcStreamTypeUnknown
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

		ctx, span := getGRPCTracer().Start(ctx, spanName,
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

		ctx, span := getGRPCTracer().Start(ctx, spanName,
			trace.WithSpanKind(trace.SpanKindClient),
		)
		defer span.End()

		span.SetAttributes(
			attribute.String(grpcServiceAttr, service),
			attribute.String(grpcMethodAttr, methodName),
			attribute.String("rpc.system", "grpc"),
			attribute.String("grpc.stream_type", func() string {
				switch {
				case desc.ClientStreams && desc.ServerStreams:
					return "bidi_stream"
				case desc.ClientStreams:
					return "client_stream"
				case desc.ServerStreams:
					return "server_stream"
				default:
					return grpcStreamTypeUnknown
				}
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
		return grpcStreamTypeUnknown, grpcStreamTypeUnknown
	}

	// Extract service name (everything after the last dot)
	serviceParts := strings.Split(parts[0], ".")
	service := serviceParts[len(serviceParts)-1]

	return service, parts[1]
}

// GRPCSpan creates a span for gRPC operations (for manual instrumentation)
func GRPCSpan(ctx context.Context, service string, method string) (context.Context, trace.Span) {
	spanName := fmt.Sprintf("%s/%s", service, method)
	ctx, span := getGRPCTracer().Start(ctx, spanName, trace.WithSpanKind(trace.SpanKindClient))

	SetAttributes(span,
		attribute.String(grpcServiceAttr, service),
		attribute.String(grpcMethodAttr, method),
		attribute.String("rpc.system", "grpc"),
	)

	return ctx, span
}
