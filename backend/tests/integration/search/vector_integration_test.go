//go:build integration

package search_test

import (
	"context"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/pgvector/pgvector-go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	vectorTestPool     *pgxpool.Pool
	vectorTestDBURL    = "postgresql://postgres:postgres@localhost:5432/tracertm_test?sslmode=disable"
	vectorSetupOnce    sync.Once
	vectorTeardownOnce sync.Once
)

func setupTestVectorSearch(t *testing.T) *pgxpool.Pool {
	vectorSetupOnce.Do(func() {
		ctx := context.Background()
		config, err := pgxpool.ParseConfig(vectorTestDBURL)
		require.NoError(t, err)

		config.MaxConns = 10
		config.MinConns = 2

		pool, err := pgxpool.NewWithConfig(ctx, config)
		require.NoError(t, err)

		err = pool.Ping(ctx)
		require.NoError(t, err)

		// Enable pgvector extension
		_, err = pool.Exec(ctx, "CREATE EXTENSION IF NOT EXISTS vector")
		require.NoError(t, err)

		// Create vector search test table
		_, err = pool.Exec(ctx, `
			CREATE TABLE IF NOT EXISTS test_embeddings (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				content TEXT NOT NULL,
				embedding vector(384), -- Common dimension for sentence transformers
				created_at TIMESTAMP DEFAULT NOW()
			);

			CREATE INDEX IF NOT EXISTS idx_test_embeddings_vector
			ON test_embeddings USING ivfflat (embedding vector_cosine_ops)
			WITH (lists = 100);
		`)
		require.NoError(t, err)

		vectorTestPool = pool
		t.Logf("✅ Test vector search database initialized successfully")
	})

	return vectorTestPool
}

func teardownTestVectorSearch(t *testing.T) {
	vectorTeardownOnce.Do(func() {
		if vectorTestPool != nil {
			ctx := context.Background()
			_, err := vectorTestPool.Exec(ctx, "DROP TABLE IF EXISTS test_embeddings CASCADE")
			if err != nil {
				t.Logf("⚠️ Warning: Failed to drop test tables: %v", err)
			}
			_ = vectorTestPool.Close()
			t.Logf("✅ Test vector search database cleaned up")
		}
	})
}

// generateRandomEmbedding generates a random normalized vector
func generateRandomEmbedding(dim int, seed int64) []float32 {
	rng := rand.New(rand.NewSource(seed))
	embedding := make([]float32, dim)
	var sumSquares float64

	// Generate random values
	for i := 0; i < dim; i++ {
		embedding[i] = float32(rng.NormFloat64())
		sumSquares += float64(embedding[i] * embedding[i])
	}

	// Normalize to unit length
	magnitude := math.Sqrt(sumSquares)
	for i := 0; i < dim; i++ {
		embedding[i] /= float32(magnitude)
	}

	return embedding
}

// generateSimilarEmbedding generates a vector similar to the base with some noise
func generateSimilarEmbedding(base []float32, similarity float64, seed int64) []float32 {
	rng := rand.New(rand.NewSource(seed))
	dim := len(base)
	result := make([]float32, dim)

	// Mix base vector with random noise
	for i := 0; i < dim; i++ {
		noise := float32(rng.NormFloat64()) * 0.1
		result[i] = base[i]*float32(similarity) + noise*float32(1-similarity)
	}

	// Normalize
	var sumSquares float64
	for i := 0; i < dim; i++ {
		sumSquares += float64(result[i] * result[i])
	}
	magnitude := math.Sqrt(sumSquares)
	for i := 0; i < dim; i++ {
		result[i] /= float32(magnitude)
	}

	return result
}

// TestVector_Indexing_WithEmbeddings tests vector indexing operations
func TestVector_Indexing_WithEmbeddings(t *testing.T) {
	pool := setupTestVectorSearch(t)
	defer teardownTestVectorSearch(t)

	ctx := context.Background()
	embeddingDim := 384

	t.Run("Insert_Single_Vector", func(t *testing.T) {
		docID := uuid.New()
		embedding := generateRandomEmbedding(embeddingDim, 12345)

		var resultID uuid.UUID
		err := pool.QueryRow(ctx, `
			INSERT INTO test_embeddings (id, title, content, embedding)
			VALUES ($1, $2, $3, $4)
			RETURNING id
		`, docID, "Test Document", "Test content", pgvector.NewVector(embedding)).Scan(&resultID)

		require.NoError(t, err)
		assert.Equal(t, docID, resultID)

		// Verify vector stored correctly
		var storedEmbedding pgvector.Vector
		err = pool.QueryRow(ctx, `
			SELECT embedding FROM test_embeddings WHERE id = $1
		`, docID).Scan(&storedEmbedding)

		require.NoError(t, err)
		assert.Equal(t, embeddingDim, len(storedEmbedding.Slice()))

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_embeddings WHERE id = $1", docID)
	})

	t.Run("Insert_Multiple_Vectors", func(t *testing.T) {
		numVectors := 100
		docIDs := make([]uuid.UUID, numVectors)

		for i := 0; i < numVectors; i++ {
			docID := uuid.New()
			docIDs[i] = docID
			embedding := generateRandomEmbedding(embeddingDim, int64(i))

			_, err := pool.Exec(ctx, `
				INSERT INTO test_embeddings (id, title, content, embedding)
				VALUES ($1, $2, $3, $4)
			`, docID, fmt.Sprintf("Document %d", i), fmt.Sprintf("Content %d", i), pgvector.NewVector(embedding))

			require.NoError(t, err)
		}

		// Verify count
		var count int
		err := pool.QueryRow(ctx, `
			SELECT COUNT(*) FROM test_embeddings WHERE id = ANY($1)
		`, docIDs).Scan(&count)

		require.NoError(t, err)
		assert.Equal(t, numVectors, count)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_embeddings WHERE id = ANY($1)", docIDs)
	})

	t.Run("Update_Vector", func(t *testing.T) {
		docID := uuid.New()
		originalEmbedding := generateRandomEmbedding(embeddingDim, 11111)

		// Insert
		_, err := pool.Exec(ctx, `
			INSERT INTO test_embeddings (id, title, content, embedding)
			VALUES ($1, $2, $3, $4)
		`, docID, "Original", "Original content", pgvector.NewVector(originalEmbedding))
		require.NoError(t, err)

		// Update with new embedding
		newEmbedding := generateRandomEmbedding(embeddingDim, 22222)
		_, err = pool.Exec(ctx, `
			UPDATE test_embeddings
			SET embedding = $2, title = $3
			WHERE id = $1
		`, docID, pgvector.NewVector(newEmbedding), "Updated")
		require.NoError(t, err)

		// Verify update
		var storedEmbedding pgvector.Vector
		var title string
		err = pool.QueryRow(ctx, `
			SELECT title, embedding FROM test_embeddings WHERE id = $1
		`, docID).Scan(&title, &storedEmbedding)

		require.NoError(t, err)
		assert.Equal(t, "Updated", title)
		assert.Equal(t, embeddingDim, len(storedEmbedding.Slice()))

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_embeddings WHERE id = $1", docID)
	})
}

// TestVector_SimilaritySearch_TopK tests vector similarity search
func TestVector_SimilaritySearch_TopK(t *testing.T) {
	pool := setupTestVectorSearch(t)
	defer teardownTestVectorSearch(t)

	ctx := context.Background()
	embeddingDim := 384

	// Create base embedding
	baseEmbedding := generateRandomEmbedding(embeddingDim, 99999)

	// Insert test vectors with varying similarity
	testDocs := []struct {
		title      string
		similarity float64
		seed       int64
	}{
		{"Very Similar", 0.95, 1001},
		{"Similar", 0.85, 1002},
		{"Somewhat Similar", 0.70, 1003},
		{"Not Very Similar", 0.50, 1004},
		{"Different", 0.30, 1005},
		{"Very Different", 0.10, 1006},
	}

	docIDs := make([]uuid.UUID, len(testDocs))

	for i, doc := range testDocs {
		docID := uuid.New()
		docIDs[i] = docID
		embedding := generateSimilarEmbedding(baseEmbedding, doc.similarity, doc.seed)

		_, err := pool.Exec(ctx, `
			INSERT INTO test_embeddings (id, title, content, embedding)
			VALUES ($1, $2, $3, $4)
		`, docID, doc.title, "Test content", pgvector.NewVector(embedding))
		require.NoError(t, err)
	}

	t.Run("TopK_Search_Cosine", func(t *testing.T) {
		k := 3
		queryEmbedding := pgvector.NewVector(baseEmbedding)

		rows, err := pool.Query(ctx, `
			SELECT id, title, 1 - (embedding <=> $1) AS similarity
			FROM test_embeddings
			WHERE id = ANY($2)
			ORDER BY embedding <=> $1
			LIMIT $3
		`, queryEmbedding, docIDs, k)
		require.NoError(t, err)
		defer rows.Close()

		var results []struct {
			id         uuid.UUID
			title      string
			similarity float64
		}

		for rows.Next() {
			var result struct {
				id         uuid.UUID
				title      string
				similarity float64
			}
			err := rows.Scan(&result.id, &result.title, &result.similarity)
			require.NoError(t, err)
			results = append(results, result)
		}

		// Verify we got top K results
		assert.Equal(t, k, len(results))

		// Verify results are ordered by similarity (descending)
		for i := 1; i < len(results); i++ {
			assert.GreaterOrEqual(t, results[i-1].similarity, results[i].similarity,
				"Results should be ordered by similarity")
		}

		// First result should be most similar
		assert.Equal(t, "Very Similar", results[0].title)
		t.Logf("Top result: %s (similarity: %.4f)", results[0].title, results[0].similarity)
	})

	t.Run("TopK_Search_L2_Distance", func(t *testing.T) {
		k := 5
		queryEmbedding := pgvector.NewVector(baseEmbedding)

		rows, err := pool.Query(ctx, `
			SELECT id, title, embedding <-> $1 AS distance
			FROM test_embeddings
			WHERE id = ANY($2)
			ORDER BY embedding <-> $1
			LIMIT $3
		`, queryEmbedding, docIDs, k)
		require.NoError(t, err)
		defer rows.Close()

		var results []struct {
			id       uuid.UUID
			title    string
			distance float64
		}

		for rows.Next() {
			var result struct {
				id       uuid.UUID
				title    string
				distance float64
			}
			err := rows.Scan(&result.id, &result.title, &result.distance)
			require.NoError(t, err)
			results = append(results, result)
		}

		assert.Equal(t, k, len(results))

		// Verify results are ordered by distance (ascending)
		for i := 1; i < len(results); i++ {
			assert.LessOrEqual(t, results[i-1].distance, results[i].distance,
				"Results should be ordered by distance")
		}

		t.Logf("Closest result: %s (distance: %.4f)", results[0].title, results[0].distance)
	})

	t.Run("Similarity_Threshold", func(t *testing.T) {
		queryEmbedding := pgvector.NewVector(baseEmbedding)
		threshold := 0.70 // Only return results with similarity >= 0.70

		rows, err := pool.Query(ctx, `
			SELECT id, title, 1 - (embedding <=> $1) AS similarity
			FROM test_embeddings
			WHERE id = ANY($2)
			AND 1 - (embedding <=> $1) >= $3
			ORDER BY embedding <=> $1
		`, queryEmbedding, docIDs, threshold)
		require.NoError(t, err)
		defer rows.Close()

		var count int
		for rows.Next() {
			var id uuid.UUID
			var title string
			var similarity float64
			err := rows.Scan(&id, &title, &similarity)
			require.NoError(t, err)
			assert.GreaterOrEqual(t, similarity, threshold)
			count++
		}

		// Should filter out low similarity results
		assert.LessOrEqual(t, count, 3)
		t.Logf("Found %d results above similarity threshold %.2f", count, threshold)
	})

	// Cleanup
	_, _ = pool.Exec(ctx, "DELETE FROM test_embeddings WHERE id = ANY($1)", docIDs)
}

// TestVector_Performance_10kVectors benchmarks vector search performance
func TestVector_Performance_10kVectors(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}

	pool := setupTestVectorSearch(t)
	defer teardownTestVectorSearch(t)

	ctx := context.Background()
	embeddingDim := 384
	numVectors := 10000

	t.Logf("Inserting %d vectors...", numVectors)
	startInsert := time.Now()

	docIDs := make([]uuid.UUID, numVectors)

	// Insert vectors in batches for better performance
	batchSize := 100
	for i := 0; i < numVectors; i += batchSize {
		end := i + batchSize
		if end > numVectors {
			end = numVectors
		}

		for j := i; j < end; j++ {
			docID := uuid.New()
			docIDs[j] = docID
			embedding := generateRandomEmbedding(embeddingDim, int64(j))

			_, err := pool.Exec(ctx, `
				INSERT INTO test_embeddings (id, title, content, embedding)
				VALUES ($1, $2, $3, $4)
			`, docID, fmt.Sprintf("Doc %d", j), fmt.Sprintf("Content %d", j), pgvector.NewVector(embedding))

			require.NoError(t, err)
		}

		if (i+batchSize)%1000 == 0 {
			t.Logf("Inserted %d vectors...", i+batchSize)
		}
	}

	insertDuration := time.Since(startInsert)
	t.Logf("Inserted %d vectors in %v (%.2f vectors/sec)",
		numVectors, insertDuration, float64(numVectors)/insertDuration.Seconds())

	// Test search performance
	t.Run("Search_Performance_TopK", func(t *testing.T) {
		queryEmbedding := generateRandomEmbedding(embeddingDim, 77777)
		k := 10

		// Warm up
		_, _ = pool.Query(ctx, `
			SELECT id FROM test_embeddings
			ORDER BY embedding <=> $1
			LIMIT $2
		`, pgvector.NewVector(queryEmbedding), k)

		// Benchmark multiple queries
		numQueries := 100
		start := time.Now()

		for i := 0; i < numQueries; i++ {
			rows, err := pool.Query(ctx, `
				SELECT id, title, 1 - (embedding <=> $1) AS similarity
				FROM test_embeddings
				ORDER BY embedding <=> $1
				LIMIT $2
			`, pgvector.NewVector(queryEmbedding), k)

			require.NoError(t, err)

			var count int
			for rows.Next() {
				var id uuid.UUID
				var title string
				var similarity float64
				err := rows.Scan(&id, &title, &similarity)
				require.NoError(t, err)
				count++
			}
			rows.Close()

			assert.Equal(t, k, count)
		}

		duration := time.Since(start)
		avgQueryTime := duration / time.Duration(numQueries)
		queriesPerSecond := float64(numQueries) / duration.Seconds()

		t.Logf("Executed %d queries in %v (avg: %v, %.2f queries/sec)",
			numQueries, duration, avgQueryTime, queriesPerSecond)

		// Performance assertions
		assert.Less(t, avgQueryTime, 100*time.Millisecond,
			"Average query time should be under 100ms")
		assert.Greater(t, queriesPerSecond, 10.0,
			"Should achieve >10 queries/sec")
	})

	t.Run("Concurrent_Search_Performance", func(t *testing.T) {
		queryEmbedding := generateRandomEmbedding(embeddingDim, 88888)
		k := 10
		numConcurrent := 10
		queriesPerWorker := 10

		var wg sync.WaitGroup
		start := time.Now()

		for i := 0; i < numConcurrent; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()

				for j := 0; j < queriesPerWorker; j++ {
					rows, err := pool.Query(ctx, `
						SELECT id FROM test_embeddings
						ORDER BY embedding <=> $1
						LIMIT $2
					`, pgvector.NewVector(queryEmbedding), k)
					if err != nil {
						t.Errorf("Query error: %v", err)
						return
					}

					for rows.Next() {
						var id uuid.UUID
						_ = rows.Scan(&id)
					}
					rows.Close()
				}
			}()
		}

		wg.Wait()
		duration := time.Since(start)

		totalQueries := numConcurrent * queriesPerWorker
		avgQueryTime := duration / time.Duration(totalQueries)
		queriesPerSecond := float64(totalQueries) / duration.Seconds()

		t.Logf("Executed %d concurrent queries in %v (avg: %v, %.2f queries/sec)",
			totalQueries, duration, avgQueryTime, queriesPerSecond)
	})

	// Cleanup
	t.Logf("Cleaning up %d vectors...", numVectors)
	_, _ = pool.Exec(ctx, "DELETE FROM test_embeddings WHERE id = ANY($1)", docIDs)
}
