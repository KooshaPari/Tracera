//go:build integration

package search_test

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	testPool     *pgxpool.Pool
	testDBURL    = "postgresql://postgres:postgres@localhost:5432/tracertm_test?sslmode=disable"
	setupOnce    sync.Once
	teardownOnce sync.Once
)

func setupTestSearch(t *testing.T) *pgxpool.Pool {
	setupOnce.Do(func() {
		ctx := context.Background()
		config, err := pgxpool.ParseConfig(testDBURL)
		require.NoError(t, err)

		config.MaxConns = 10
		config.MinConns = 2

		pool, err := pgxpool.NewWithConfig(ctx, config)
		require.NoError(t, err)

		err = pool.Ping(ctx)
		require.NoError(t, err)

		// Create full-text search test table
		_, err = pool.Exec(ctx, `
			CREATE TABLE IF NOT EXISTS test_documents (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				content TEXT NOT NULL,
				category TEXT,
				tags TEXT[],
				search_vector tsvector GENERATED ALWAYS AS (
					setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
					setweight(to_tsvector('english', coalesce(content, '')), 'B') ||
					setweight(to_tsvector('english', coalesce(category, '')), 'C')
				) STORED,
				created_at TIMESTAMP DEFAULT NOW()
			);

			CREATE INDEX IF NOT EXISTS idx_test_documents_search ON test_documents USING GIN(search_vector);
			CREATE INDEX IF NOT EXISTS idx_test_documents_tags ON test_documents USING GIN(tags);
		`)
		require.NoError(t, err)

		testPool = pool
		t.Logf("✅ Test search database initialized successfully")
	})

	return testPool
}

func teardownTestSearch(t *testing.T) {
	teardownOnce.Do(func() {
		if testPool != nil {
			ctx := context.Background()
			_, err := testPool.Exec(ctx, "DROP TABLE IF EXISTS test_documents CASCADE")
			if err != nil {
				t.Logf("⚠️ Warning: Failed to drop test tables: %v", err)
			}
			_ = testPool.Close()
			t.Logf("✅ Test search database cleaned up")
		}
	})
}

// TestFullText_Indexing_Success tests document indexing for full-text search
func TestFullText_Indexing_Success(t *testing.T) {
	pool := setupTestSearch(t)
	defer teardownTestSearch(t)

	ctx := context.Background()

	t.Run("Single_Document", func(t *testing.T) {
		docID := uuid.New()
		title := "Introduction to Go Programming"
		content := "Go is a statically typed, compiled programming language designed at Google."

		var resultID uuid.UUID
		err := pool.QueryRow(ctx, `
			INSERT INTO test_documents (id, title, content, category)
			VALUES ($1, $2, $3, $4)
			RETURNING id
		`, docID, title, content, "Programming").Scan(&resultID)

		require.NoError(t, err)
		assert.Equal(t, docID, resultID)

		// Verify search vector was generated
		var hasVector bool
		err = pool.QueryRow(ctx, `
			SELECT search_vector IS NOT NULL
			FROM test_documents
			WHERE id = $1
		`, docID).Scan(&hasVector)

		require.NoError(t, err)
		assert.True(t, hasVector)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = $1", docID)
	})

	t.Run("Batch_Indexing", func(t *testing.T) {
		documents := []struct {
			title    string
			content  string
			category string
			tags     []string
		}{
			{"Go Concurrency", "Goroutines and channels make concurrent programming easy", "Programming", []string{"go", "concurrency"}},
			{"Database Optimization", "Indexing strategies for PostgreSQL performance", "Database", []string{"postgres", "performance"}},
			{"API Design", "RESTful API best practices and patterns", "Architecture", []string{"api", "rest"}},
			{"Testing Strategies", "Unit testing and integration testing in Go", "Testing", []string{"go", "testing"}},
			{"Microservices", "Building microservices with Go and gRPC", "Architecture", []string{"go", "grpc"}},
		}

		docIDs := make([]uuid.UUID, len(documents))

		for i, doc := range documents {
			docID := uuid.New()
			docIDs[i] = docID

			err := pool.QueryRow(ctx, `
				INSERT INTO test_documents (id, title, content, category, tags)
				VALUES ($1, $2, $3, $4, $5)
				RETURNING id
			`, docID, doc.title, doc.content, doc.category, doc.tags).Scan(&docID)

			require.NoError(t, err)
		}

		// Verify all indexed
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*) FROM test_documents WHERE id = ANY($1)
		`, docIDs).Scan(&count)

		require.NoError(t, err)
		assert.Equal(t, len(documents), count)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = ANY($1)", docIDs)
	})

	t.Run("Update_Document", func(t *testing.T) {
		docID := uuid.New()

		// Insert original
		_, err := pool.Exec(ctx, `
			INSERT INTO test_documents (id, title, content, category)
			VALUES ($1, $2, $3, $4)
		`, docID, "Original Title", "Original content", "Test")
		require.NoError(t, err)

		// Update document
		_, err = pool.Exec(ctx, `
			UPDATE test_documents
			SET title = $2, content = $3
			WHERE id = $1
		`, docID, "Updated Title", "Updated content with new keywords")
		require.NoError(t, err)

		// Search should find updated content
		var foundID uuid.UUID
		err = pool.QueryRow(ctx, `
			SELECT id FROM test_documents
			WHERE search_vector @@ to_tsquery('english', 'keywords')
			AND id = $1
		`, docID).Scan(&foundID)

		require.NoError(t, err)
		assert.Equal(t, docID, foundID)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = $1", docID)
	})
}

// TestFullText_Query_Ranking tests search result ranking
func TestFullText_Query_Ranking(t *testing.T) {
	pool := setupTestSearch(t)
	defer teardownTestSearch(t)

	ctx := context.Background()

	// Insert test documents with different relevance
	documents := []struct {
		title   string
		content string
	}{
		{"PostgreSQL Database", "Advanced PostgreSQL features"},                   // Exact match in title
		{"Database Systems", "PostgreSQL is a powerful database system"},          // Match in content
		{"SQL Queries", "Writing efficient SQL queries for PostgreSQL databases"}, // Multiple matches
		{"NoSQL Databases", "MongoDB and other NoSQL database solutions"},         // Low relevance
		{"PostgreSQL Performance", "Optimizing PostgreSQL for high performance"},  // Multiple matches with high weight
	}

	docIDs := make([]uuid.UUID, len(documents))

	for i, doc := range documents {
		docID := uuid.New()
		docIDs[i] = docID

		_, err := pool.Exec(ctx, `
			INSERT INTO test_documents (id, title, content, category)
			VALUES ($1, $2, $3, $4)
		`, docID, doc.title, doc.content, "Test")
		require.NoError(t, err)
	}

	// Search with ranking
	rows, err := pool.Query(ctx, `
		SELECT id, title,
			   ts_rank(search_vector, to_tsquery('english', 'PostgreSQL')) AS rank
		FROM test_documents
		WHERE search_vector @@ to_tsquery('english', 'PostgreSQL')
		ORDER BY rank DESC
	`)
	require.NoError(t, err)
	defer rows.Close()

	var results []struct {
		id    uuid.UUID
		title string
		rank  float32
	}

	for rows.Next() {
		var result struct {
			id    uuid.UUID
			title string
			rank  float32
		}
		err := rows.Scan(&result.id, &result.title, &result.rank)
		require.NoError(t, err)
		results = append(results, result)
	}

	// Verify ranking order (titles with PostgreSQL should rank higher)
	assert.GreaterOrEqual(t, len(results), 3, "Should find at least 3 documents")

	if len(results) >= 2 {
		// First result should have higher rank than second
		assert.Greater(t, results[0].rank, results[len(results)-1].rank)
		t.Logf("Top result: %s (rank: %.4f)", results[0].title, results[0].rank)
	}

	// Cleanup
	_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = ANY($1)", docIDs)
}

// TestFullText_BooleanOperators tests boolean search operators
func TestFullText_BooleanOperators(t *testing.T) {
	pool := setupTestSearch(t)
	defer teardownTestSearch(t)

	ctx := context.Background()

	// Insert test documents
	documents := []struct {
		title   string
		content string
	}{
		{"Go and PostgreSQL", "Building applications with Go and PostgreSQL"},
		{"Go Programming", "Advanced Go programming techniques"},
		{"PostgreSQL Administration", "Database administration with PostgreSQL"},
		{"Python and PostgreSQL", "Using Python with PostgreSQL databases"},
	}

	docIDs := make([]uuid.UUID, len(documents))

	for i, doc := range documents {
		docID := uuid.New()
		docIDs[i] = docID

		_, err := pool.Exec(ctx, `
			INSERT INTO test_documents (id, title, content, category)
			VALUES ($1, $2, $3, $4)
		`, docID, doc.title, doc.content, "Test")
		require.NoError(t, err)
	}

	t.Run("AND_Operator", func(t *testing.T) {
		// Search for documents with both "Go" AND "PostgreSQL"
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*)
			FROM test_documents
			WHERE search_vector @@ to_tsquery('english', 'Go & PostgreSQL')
		`).Scan(&count)

		require.NoError(t, err)
		assert.Equal(t, 1, count) // Only "Go and PostgreSQL" should match
	})

	t.Run("OR_Operator", func(t *testing.T) {
		// Search for documents with "Go" OR "Python"
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*)
			FROM test_documents
			WHERE search_vector @@ to_tsquery('english', 'Go | Python')
		`).Scan(&count)

		require.NoError(t, err)
		assert.GreaterOrEqual(t, count, 3) // Should find Go and Python documents
	})

	t.Run("NOT_Operator", func(t *testing.T) {
		// Search for "PostgreSQL" but NOT "Python"
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*)
			FROM test_documents
			WHERE search_vector @@ to_tsquery('english', 'PostgreSQL & !Python')
		`).Scan(&count)

		require.NoError(t, err)
		assert.GreaterOrEqual(t, count, 2) // Should exclude Python document
	})

	t.Run("Phrase_Search", func(t *testing.T) {
		// Search for phrase "Advanced Go programming"
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*)
			FROM test_documents
			WHERE search_vector @@ phraseto_tsquery('english', 'Advanced Go programming')
		`).Scan(&count)

		require.NoError(t, err)
		assert.GreaterOrEqual(t, count, 1)
	})

	// Cleanup
	_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = ANY($1)", docIDs)
}

// TestFullText_Performance_LargeDataset benchmarks search performance
func TestFullText_Performance_LargeDataset(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	pool := setupTestSearch(t)
	defer teardownTestSearch(t)

	ctx := context.Background()

	// Insert large dataset
	numDocs := 10000
	docIDs := make([]uuid.UUID, numDocs)

	t.Logf("Inserting %d test documents...", numDocs)
	startInsert := time.Now()

	for i := 0; i < numDocs; i++ {
		docID := uuid.New()
		docIDs[i] = docID

		title := fmt.Sprintf("Document %d about %s", i, getRandomTopic(i))
		content := fmt.Sprintf("This is document number %d containing information about %s and related topics", i, getRandomTopic(i))

		_, err := pool.Exec(ctx, `
			INSERT INTO test_documents (id, title, content, category)
			VALUES ($1, $2, $3, $4)
		`, docID, title, content, getRandomCategory(i))
		require.NoError(t, err)
	}

	insertDuration := time.Since(startInsert)
	t.Logf("Inserted %d documents in %v (%.2f docs/sec)", numDocs, insertDuration, float64(numDocs)/insertDuration.Seconds())

	// Test search performance
	t.Run("Simple_Search_Performance", func(t *testing.T) {
		queries := []string{"database", "programming", "performance", "optimization", "testing"}

		for _, query := range queries {
			start := time.Now()

			var count int
			err := pool.QueryRow(ctx, `
				SELECT COUNT(*)
				FROM test_documents
				WHERE search_vector @@ to_tsquery('english', $1)
			`, query).Scan(&count)

			duration := time.Since(start)
			require.NoError(t, err)

			t.Logf("Query '%s' found %d results in %v", query, count, duration)
			assert.Less(t, duration, 100*time.Millisecond, "Search should complete in <100ms")
		}
	})

	t.Run("Ranked_Search_Performance", func(t *testing.T) {
		start := time.Now()

		rows, err := pool.Query(ctx, `
			SELECT id, title, ts_rank(search_vector, to_tsquery('english', 'database')) AS rank
			FROM test_documents
			WHERE search_vector @@ to_tsquery('english', 'database')
			ORDER BY rank DESC
			LIMIT 10
		`)
		require.NoError(t, err)
		defer rows.Close()

		var results int
		for rows.Next() {
			var id uuid.UUID
			var title string
			var rank float32
			err := rows.Scan(&id, &title, &rank)
			require.NoError(t, err)
			results++
		}

		duration := time.Since(start)
		t.Logf("Ranked search found %d results in %v", results, duration)
		assert.Less(t, duration, 100*time.Millisecond, "Ranked search should complete in <100ms")
		assert.Equal(t, 10, results)
	})

	// Cleanup
	t.Logf("Cleaning up %d test documents...", numDocs)
	_, _ = pool.Exec(ctx, "DELETE FROM test_documents WHERE id = ANY($1)", docIDs)
}

// Helper functions for test data generation
func getRandomTopic(index int) string {
	topics := []string{
		"database optimization",
		"programming languages",
		"performance tuning",
		"software architecture",
		"testing strategies",
		"API design",
		"microservices",
		"cloud computing",
		"data structures",
		"algorithms",
	}
	return topics[index%len(topics)]
}

func getRandomCategory(index int) string {
	categories := []string{
		"Database",
		"Programming",
		"Architecture",
		"Testing",
		"DevOps",
	}
	return categories[index%len(categories)]
}
