package integration

import (
	"context"
	"testing"

	"github.com/kooshapari/tracertm-backend/tests/testutil"
)

// TestFullEnvironment demonstrates using the complete test environment
func TestFullEnvironment(t *testing.T) {
	ctx := context.Background()

	// Create full test environment (PostgreSQL, Redis, Neo4j, NATS)
	env, err := testutil.NewTestEnvironment(ctx)
	if err != nil {
		t.Fatalf("failed to create test environment: %v", err)
	}
	defer env.Cleanup(ctx)

	// Environment is ready with all services and migrations applied
	t.Run("verify_postgres", func(t *testing.T) {
		testutil.AssertNotNil(t, env.PostgresPool, "postgres pool should be initialized")

		// Create test data
		projectID, err := testutil.CreateTestProject(ctx, env.PostgresPool, "Test Project")
		testutil.AssertNoError(t, err, "should create project")
		testutil.AssertNotNil(t, projectID, "project ID should not be nil")
	})

	t.Run("verify_nats", func(t *testing.T) {
		testutil.AssertNotNil(t, env.NATSConn, "nats connection should be initialized")
		testutil.AssertEqual(t, true, env.NATSConn.IsConnected(), "nats should be connected")
	})

	t.Run("verify_config", func(t *testing.T) {
		testutil.AssertNotNil(t, env.Config, "config should be initialized")
		testutil.AssertNotEqual(t, "", env.Config.PostgresURL, "postgres URL should be set")
		testutil.AssertNotEqual(t, "", env.Config.RedisURL, "dragonfly-compatible URL should be set")
		testutil.AssertNotEqual(t, "", env.Config.Neo4jURL, "neo4j URL should be set")
		testutil.AssertNotEqual(t, "", env.Config.NATSURL, "nats URL should be set")
	})

	// Reset database between tests
	t.Run("reset_database", func(t *testing.T) {
		// Create some data
		projectID, err := testutil.CreateTestProject(ctx, env.PostgresPool, "Test Project 1")
		testutil.AssertNoError(t, err, "should create project")

		// Reset database
		err = env.ResetDatabase(ctx)
		testutil.AssertNoError(t, err, "should reset database")

		// Verify data was cleared
		project, err := testutil.GetProjectByID(ctx, env.PostgresPool, projectID)
		testutil.AssertError(t, err, "project should not exist after reset")
		testutil.AssertNil(t, project, "project should be nil")
	})
}

// TestMinimalEnvironment demonstrates using a minimal test environment
func TestMinimalEnvironment(t *testing.T) {
	ctx := context.Background()

	// Create minimal environment (only PostgreSQL)
	env, err := testutil.NewMinimalTestEnvironment(ctx)
	if err != nil {
		t.Fatalf("failed to create minimal environment: %v", err)
	}
	defer env.Cleanup(ctx)

	// Only PostgreSQL services are available
	testutil.AssertNotNil(t, env.PostgresPool, "postgres pool should be initialized")
	testutil.AssertNil(t, env.NATSConn, "nats should not be initialized")
	testutil.AssertNil(t, env.DragonflyContainer, "dragonfly should not be started")
	testutil.AssertNil(t, env.Neo4jContainer, "neo4j should not be started")

	// Run tests with PostgreSQL only
	projectID, err := testutil.CreateTestProject(ctx, env.PostgresPool, "Minimal Test")
	testutil.AssertNoError(t, err, "should create project")
	testutil.AssertNotNil(t, projectID, "project ID should not be nil")
}

// TestEnvironmentWithSubtests demonstrates reusing environment across subtests
func TestEnvironmentWithSubtests(t *testing.T) {
	ctx := context.Background()

	env, err := testutil.NewTestEnvironment(ctx)
	if err != nil {
		t.Fatalf("failed to create test environment: %v", err)
	}
	defer env.Cleanup(ctx)

	tests := []struct {
		name        string
		projectName string
	}{
		{"project1", "Project Alpha"},
		{"project2", "Project Beta"},
		{"project3", "Project Gamma"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each subtest
			defer env.ResetDatabase(ctx)

			projectID, err := testutil.CreateTestProject(ctx, env.PostgresPool, tt.projectName)
			testutil.AssertNoError(t, err, "should create project")

			project, err := testutil.GetProjectByID(ctx, env.PostgresPool, projectID)
			testutil.AssertNoError(t, err, "should retrieve project")
			testutil.AssertEqual(t, tt.projectName, project["name"], "project name should match")
		})
	}
}

// TestEventPublishing demonstrates NATS event testing
func TestEventPublishing(t *testing.T) {
	ctx := context.Background()

	env, err := testutil.NewTestEnvironment(ctx)
	if err != nil {
		t.Fatalf("failed to create test environment: %v", err)
	}
	defer env.Cleanup(ctx)

	// Publish a test event
	err = env.NATSConn.Publish("project.created", []byte(`{"project_id":"123","name":"Test"}`))
	testutil.AssertNoError(t, err, "should publish event")

	// Verify event was published
	err = testutil.AssertEventPublished(t, "project.created", env.NATSConn)
	testutil.AssertNoError(t, err, "event should be published")
}
