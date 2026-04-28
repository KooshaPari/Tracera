package tracing

// ExampleHTTPHandlerInstrumentation demonstrates how to instrument an HTTP handler
// with OpenTelemetry tracing.
//
// Example usage in an Echo handler:
//
//	func MyHandler(c echo.Context) error {
//	    ctx, span := tracing.HTTPSpan(c.Request().Context(), "GET", "/api/items")
//	    defer span.End()
//
//	    items, err := service.ListItems(ctx)
//	    if err != nil {
//	        tracing.RecordError(span, err)
//	        return c.JSON(http.StatusInternalServerError, err)
//	    }
//
//	    tracing.SetHTTPStatus(span, http.StatusOK)
//	    return c.JSON(http.StatusOK, items)
//	}
func ExampleHTTPHandlerInstrumentation() {}

// ExampleDatabaseOperationInstrumentation demonstrates how to instrument database operations.
//
// Example usage:
//
//	func GetUserByID(ctx context.Context, userID string) (*User, error) {
//	    ctx, span := tracing.DatabaseSpan(ctx, "SELECT", "users")
//	    defer span.End()
//
//	    tracing.SetAttributes(span, attribute.String("user.id", userID))
//
//	    user := &User{}
//	    if err := db.WithContext(ctx).First(user, userID).Error; err != nil {
//	        tracing.RecordError(span, err)
//	        return nil, err
//	    }
//	    return user, nil
//	}
func ExampleDatabaseOperationInstrumentation() {}

// ExampleGRPCCallInstrumentation demonstrates how to instrument gRPC calls.
//
// Example usage:
//
//	func (h *Handler) AnalyzeGraph(ctx context.Context, itemID string) error {
//	    ctx, span := tracing.GRPCSpan(ctx, "GraphService", "AnalyzeImpact")
//	    defer span.End()
//
//	    tracing.SetAttributes(span,
//	        attribute.String("item.id", itemID),
//	        attribute.String("direction", "downstream"),
//	    )
//
//	    req := &pb.AnalyzeImpactRequest{
//	        ItemId: itemID,
//	        Direction: "downstream",
//	    }
//	    resp, err := h.grpcClient.AnalyzeImpact(ctx, req)
//	    if err != nil {
//	        tracing.RecordError(span, err)
//	        return err
//	    }
//	    return nil
//	}
func ExampleGRPCCallInstrumentation() {}

// ExampleCacheOperationInstrumentation demonstrates how to instrument cache operations.
//
// Example usage:
//
//	func GetCachedProject(ctx context.Context, projectID string) (*Project, error) {
//	    cacheKey := "project:" + projectID
//	    ctx, span := tracing.CacheSpan(ctx, "GET", cacheKey)
//	    defer span.End()
//
//	    val, err := cache.Get(ctx, cacheKey)
//	    if err != nil {
//	        tracing.AddEvent(span, "cache.miss")
//	        return nil, err
//	    }
//	    tracing.AddEvent(span, "cache.hit")
//	    return val, nil
//	}
func ExampleCacheOperationInstrumentation() {}

// ExampleAsyncOperationInstrumentation demonstrates how to instrument async operations
// while preserving trace context.
//
// Example usage:
//
//	func ProcessItemAsync(ctx context.Context, itemID string) error {
//	    // Preserve trace context for async operation
//	    asyncCtx := tracing.WrapAsync(ctx)
//	    ctx, _ = tracing.WithProjectID(ctx, projectID)
//
//	    go func() {
//	        ctx, span := tracing.StartSpan(asyncCtx, "async.process_item")
//	        defer span.End()
//
//	        tracing.SetProjectID(span, projectID)
//	        tracing.SetAttributes(span, attribute.String("item.id", itemID))
//
//	        if err := processItem(ctx, itemID); err != nil {
//	            tracing.RecordError(span, err)
//	        }
//	    }()
//	    return nil
//	}
func ExampleAsyncOperationInstrumentation() {}

// ExampleContextPropagation demonstrates how to propagate trace context across
// service boundaries.
//
// Example usage:
//
//	func MakeExternalCall(ctx context.Context, url string) ([]byte, error) {
//	    ctx, span := tracing.HTTPSpan(ctx, "POST", url)
//	    defer span.End()
//
//	    req, _ := http.NewRequestWithContext(ctx, "POST", url, nil)
//	    // Trace context is automatically propagated via headers
//	    // (OpenTelemetry HTTP client instrumentation handles this)
//
//	    resp, err := http.DefaultClient.Do(req)
//	    if err != nil {
//	        tracing.RecordError(span, err)
//	        return nil, err
//	    }
//	    defer resp.Body.Close()
//
//	    tracing.SetHTTPStatus(span, resp.StatusCode)
//	    return io.ReadAll(resp.Body)
//	}
func ExampleContextPropagation() {}

// ExampleSpanWithMultipleAttributes demonstrates how to add detailed attributes to spans.
//
// Example usage:
//
//	func CreateProject(ctx context.Context, req *CreateProjectRequest) (*Project, error) {
//	    ctx, span := tracing.StartSpan(ctx, "project.create")
//	    defer span.End()
//
//	    // Add detailed attributes
//	    tracing.SetAttributes(span,
//	        attribute.String("project.name", req.Name),
//	        attribute.String("user.id", req.UserID),
//	        attribute.Int("initial_capacity", req.Capacity),
//	        attribute.Bool("is_public", req.Public),
//	    )
//
//	    // Add events for tracking progress
//	    tracing.AddEvent(span, "validation.start")
//	    if err := validateRequest(req); err != nil {
//	        tracing.AddEvent(span, "validation.failed",
//	            attribute.String("error", err.Error()),
//	        )
//	        tracing.RecordError(span, err)
//	        return nil, err
//	    }
//	    tracing.AddEvent(span, "validation.passed")
//
//	    // Create project
//	    tracing.AddEvent(span, "db.insert.start")
//	    project := &Project{
//	        Name:     req.Name,
//	        UserID:   req.UserID,
//	        Public:   req.Public,
//	        Capacity: req.Capacity,
//	    }
//	    if err := db.Create(project).Error; err != nil {
//	        tracing.AddEvent(span, "db.insert.failed")
//	        tracing.RecordError(span, err)
//	        return nil, err
//	    }
//	    tracing.AddEvent(span, "db.insert.success",
//	        attribute.String("project.id", project.ID),
//	    )
//
//	    return project, nil
//	}
func ExampleSpanWithMultipleAttributes() {}

// ExampleGRPCServerInstrumentation demonstrates automatic gRPC server instrumentation.
// This happens transparently when the server is created with OpenTelemetry interceptors.
//
// In internal/grpc/server.go:
//
//	grpcServer := grpc.NewServer(
//	    // ... other options
//	    grpc.UnaryInterceptor(tracing.UnaryServerInterceptor()),
//	    grpc.StreamInterceptor(tracing.StreamServerInterceptor()),
//	)
//
// After this, every gRPC call will automatically create a span with:
// - Service name extracted from method path
// - Method name extracted from method path
// - User ID and project ID from metadata (if present)
// - gRPC status code recorded on completion
// - Errors recorded if the call fails
func ExampleGRPCServerInstrumentation() {}

// ExampleTemporalWorkflowInstrumentation demonstrates how to instrument Temporal workflows.
//
// Example usage:
//
//	func ExecuteProcessWorkflow(ctx context.Context, processID string) error {
//	    ctx, span := tracing.TemporalSpan(ctx, "ProcessWorkflow", processID)
//	    defer span.End()
//
//	    tracing.SetAttributes(span,
//	        attribute.String("process.id", processID),
//	        attribute.String("workflow.status", "started"),
//	    )
//
//	    // Execute workflow steps...
//
//	    tracing.AddEvent(span, "workflow.completed",
//	        attribute.String("workflow.status", "success"),
//	    )
//	    return nil
//	}
func ExampleTemporalWorkflowInstrumentation() {}

// ExampleNATSMessagingInstrumentation demonstrates how to instrument NATS operations.
//
// Example usage:
//
//	func PublishProjectEvent(ctx context.Context, event *ProjectEvent) error {
//	    subject := "project.events." + event.ProjectID
//	    ctx, span := tracing.NATSSpan(ctx, "PUBLISH", subject)
//	    defer span.End()
//
//	    tracing.SetAttributes(span,
//	        attribute.String("event.type", event.Type),
//	        attribute.String("project.id", event.ProjectID),
//	    )
//
//	    data, _ := json.Marshal(event)
//	    if err := natsClient.Publish(subject, data); err != nil {
//	        tracing.RecordError(span, err)
//	        return err
//	    }
//	    return nil
//	}
func ExampleNATSMessagingInstrumentation() {}

// ExampleAIAgentInstrumentation demonstrates how to instrument AI agent operations.
//
// Example usage:
//
//	func RunAnalysisAgent(ctx context.Context, itemID string) (string, error) {
//	    ctx, span := tracing.AIAgentSpan(ctx, "analysis", "run")
//	    defer span.End()
//
//	    tracing.SetAttributes(span,
//	        attribute.String("item.id", itemID),
//	        attribute.String("agent.model", "gpt-4"),
//	    )
//
//	    tracing.AddEvent(span, "agent.execution.start")
//
//	    result, err := agent.Execute(ctx, itemID)
//	    if err != nil {
//	        tracing.AddEvent(span, "agent.execution.failed")
//	        tracing.RecordError(span, err)
//	        return "", err
//	    }
//
//	    tracing.AddEvent(span, "agent.execution.complete",
//	        attribute.String("result.length", string(rune(len(result)))),
//	    )
//	    return result, nil
//	}
func ExampleAIAgentInstrumentation() {}
