package temporal

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/minio/minio-go/v7"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
	"go.uber.org/zap"
)

// Service wraps Temporal client and worker lifecycle
type Service struct {
	client     client.Client
	worker     worker.Worker
	activities *SnapshotActivities
	logger     *zap.Logger
}

// Config contains dependencies for Temporal service
type Config struct {
	TemporalHost string
	Namespace    string
	TaskQueue    string
	DB           *sql.DB
	Neo4j        neo4j.Driver //nolint:staticcheck // SA1019: DriverWithContext migration tracked separately
	MinIO        *minio.Client
	Logger       *zap.Logger
}

// NewService creates a new Temporal service instance
func NewService(cfg *Config) (*Service, error) {
	// Create Temporal client
	client, err := client.Dial(client.Options{
		HostPort:  cfg.TemporalHost,
		Namespace: cfg.Namespace,
		Logger:    NewZapAdapter(cfg.Logger),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create Temporal client: %worker", err)
	}

	// Create snapshot activities
	activities := NewSnapshotActivities(cfg.DB, cfg.Neo4j, cfg.MinIO, cfg.Logger)

	// Create worker
	worker := worker.New(client, cfg.TaskQueue, worker.Options{
		MaxConcurrentActivityExecutionSize: 10,
	})

	// Register workflows
	worker.RegisterWorkflow(SnapshotWorkflow)
	worker.RegisterWorkflow(ScheduledSnapshotWorkflow)

	// Register activities
	worker.RegisterActivity(activities.QuerySnapshot)
	worker.RegisterActivity(activities.CreateSnapshot)
	worker.RegisterActivity(activities.UploadSnapshot)

	return &Service{
		client:     client,
		worker:     worker,
		activities: activities,
		logger:     cfg.Logger,
	}, nil
}

// Start begins the Temporal worker
func (s *Service) Start() error {
	s.logger.Info("Starting Temporal worker")
	return s.worker.Start()
}

// Stop gracefully shuts down the worker and client
func (s *Service) Stop() {
	s.logger.Info("Stopping Temporal worker")
	s.worker.Stop()
	s.client.Close()
}

// TriggerSnapshot triggers a snapshot workflow for a session
func (s *Service) TriggerSnapshot(ctx context.Context, sessionID string) (string, error) {
	workflowID := fmt.Sprintf("snapshot-%s-%d", sessionID, nowUnixMilli())
	workflowOptions := client.StartWorkflowOptions{
		ID:        workflowID,
		TaskQueue: "snapshot-tasks",
	}

	req := SnapshotRequest{SessionID: sessionID}
	we, err := s.client.ExecuteWorkflow(ctx, workflowOptions, SnapshotWorkflow, req)
	if err != nil {
		return "", fmt.Errorf("failed to start snapshot workflow: %w", err)
	}

	// Wait for result
	var s3Key string
	err = we.Get(ctx, &s3Key)
	if err != nil {
		return "", fmt.Errorf("snapshot workflow failed: %w", err)
	}

	s.logger.Info("Snapshot workflow completed",
		zap.String("workflow_id", workflowID),
		zap.String("session_id", sessionID),
		zap.String("s3_key", s3Key))

	return s3Key, nil
}

// ZapAdapter adapts zap.Logger to Temporal's logger interface
type ZapAdapter struct {
	logger *zap.Logger
}

// NewZapAdapter creates a new ZapAdapter
func NewZapAdapter(logger *zap.Logger) *ZapAdapter {
	return &ZapAdapter{logger: logger}
}

// Debug logs a debug-level message with optional key-value pairs.
func (z *ZapAdapter) Debug(msg string, keyvals ...interface{}) {
	z.logger.Debug(msg, toZapFields(keyvals)...)
}

// Info logs an info-level message with optional key-value pairs.
func (z *ZapAdapter) Info(msg string, keyvals ...interface{}) {
	z.logger.Info(msg, toZapFields(keyvals)...)
}

// Warn logs a warn-level message with optional key-value pairs.
func (z *ZapAdapter) Warn(msg string, keyvals ...interface{}) {
	z.logger.Warn(msg, toZapFields(keyvals)...)
}

func (z *ZapAdapter) Error(msg string, keyvals ...interface{}) {
	z.logger.Error(msg, toZapFields(keyvals)...)
}

// toZapFields converts key-value pairs to zap fields
func toZapFields(keyvals []interface{}) []zap.Field {
	fields := make([]zap.Field, 0, len(keyvals)/2)
	for i := 0; i < len(keyvals); i += 2 {
		if i+1 < len(keyvals) {
			key, ok := keyvals[i].(string)
			if !ok {
				continue
			}
			fields = append(fields, zap.Any(key, keyvals[i+1]))
		}
	}
	return fields
}

// nowUnixMilli returns current Unix time in milliseconds
func nowUnixMilli() int64 {
	return time.Now().UnixMilli()
}
