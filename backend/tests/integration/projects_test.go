package integration

import (
	"context"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/tests/testutil"
)

// TestProjectCreation demonstrates integration testing with testcontainers
func TestProjectCreation(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
	container, connString, err := testutil.PostgresContainer(ctx)
	if err != nil {
		t.Fatalf("failed to start postgres container: %v", err)
	}
	defer container.Terminate(ctx)

	// Connect to database
	pool, err := pgxpool.New(ctx, connString)
	if err != nil {
		t.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Run migrations
	err = testutil.ExecuteMigrations(ctx, pool, "../../schema.sql")
	if err != nil {
		t.Fatalf("failed to run migrations: %v", err)
	}

	// Test project creation
	projectID, err := testutil.CreateTestProject(ctx, pool, "Integration Test Project")
	testutil.AssertNoError(t, err, "should create project")
	testutil.AssertNotNil(t, projectID, "project ID should not be nil")

	// Verify project was created
	project, err := testutil.GetProjectByID(ctx, pool, projectID)
	testutil.AssertNoError(t, err, "should retrieve project")
	testutil.AssertEqual(t, "Integration Test Project", project["name"], "project name should match")
}

// TestItemCreation demonstrates creating items within a project
func TestItemCreation(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
	container, connString, err := testutil.PostgresContainer(ctx)
	if err != nil {
		t.Fatalf("failed to start postgres container: %v", err)
	}
	defer container.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	if err != nil {
		t.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Run migrations
	err = testutil.ExecuteMigrations(ctx, pool, "../../schema.sql")
	if err != nil {
		t.Fatalf("failed to run migrations: %v", err)
	}

	// Create test project
	projectID, err := testutil.CreateTestProject(ctx, pool, "Test Project")
	testutil.AssertNoError(t, err, "should create project")

	// Test item creation
	itemID, err := testutil.CreateTestItem(ctx, pool, projectID, "Test Item")
	testutil.AssertNoError(t, err, "should create item")
	testutil.AssertNotNil(t, itemID, "item ID should not be nil")

	// Verify item was created
	item, err := testutil.GetItemByID(ctx, pool, itemID)
	testutil.AssertNoError(t, err, "should retrieve item")
	testutil.AssertEqual(t, "Test Item", item["title"], "item title should match")
	testutil.AssertEqual(t, projectID, item["project_id"], "item should belong to project")
}

// TestLinkCreation demonstrates creating links between items
func TestLinkCreation(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
	container, connString, err := testutil.PostgresContainer(ctx)
	if err != nil {
		t.Fatalf("failed to start postgres container: %v", err)
	}
	defer container.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	if err != nil {
		t.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Run migrations
	err = testutil.ExecuteMigrations(ctx, pool, "../../schema.sql")
	if err != nil {
		t.Fatalf("failed to run migrations: %v", err)
	}

	// Create test data
	projectID, err := testutil.CreateTestProject(ctx, pool, "Test Project")
	testutil.AssertNoError(t, err, "should create project")

	sourceID, err := testutil.CreateTestItem(ctx, pool, projectID, "Source Item")
	testutil.AssertNoError(t, err, "should create source item")

	targetID, err := testutil.CreateTestItem(ctx, pool, projectID, "Target Item")
	testutil.AssertNoError(t, err, "should create target item")

	// Test link creation
	linkID, err := testutil.CreateTestLink(ctx, pool, sourceID, targetID)
	testutil.AssertNoError(t, err, "should create link")
	testutil.AssertNotNil(t, linkID, "link ID should not be nil")
}

// TestSuiteWithContainerReuse demonstrates reusing containers across subtests
func TestSuiteWithContainerReuse(t *testing.T) {
	ctx := context.Background()

	// Start container once for all subtests
	container, connString, err := testutil.PostgresContainer(ctx)
	if err != nil {
		t.Fatalf("failed to start postgres container: %v", err)
	}
	defer container.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	if err != nil {
		t.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Run migrations once
	err = testutil.ExecuteMigrations(ctx, pool, "../../src/schema.sql")
	if err != nil {
		t.Fatalf("failed to run migrations: %v", err)
	}

	t.Run("test1", func(t *testing.T) {
		defer testutil.TruncateAllTables(ctx, pool)

		projectID, err := testutil.CreateTestProject(ctx, pool, "Project 1")
		testutil.AssertNoError(t, err, "should create project")
		testutil.AssertNotNil(t, projectID, "project ID should not be nil")
	})

	t.Run("test2", func(t *testing.T) {
		defer testutil.TruncateAllTables(ctx, pool)

		projectID, err := testutil.CreateTestProject(ctx, pool, "Project 2")
		testutil.AssertNoError(t, err, "should create project")
		testutil.AssertNotNil(t, projectID, "project ID should not be nil")
	})
}

// TestWithMockServers demonstrates using mock HTTP servers
func TestWithMockServers(t *testing.T) {
	// Start mock servers
	supabaseServer := testutil.MockSupabaseServer()
	defer supabaseServer.Close()

	voyageServer := testutil.MockVoyageAIServer()
	defer voyageServer.Close()

	// Use mock server URLs in tests
	t.Logf("Supabase URL: %s", supabaseServer.URL)
	t.Logf("VoyageAI URL: %s", voyageServer.URL)

	// Your integration tests using these mock servers would go here
}
