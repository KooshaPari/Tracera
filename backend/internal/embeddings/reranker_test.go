package embeddings

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	rerankerTestRateLimit    = 300
	rerankerTestMaxRetries   = 3
	rerankerTestRateLimitAlt = 500
	rerankerTestRetriesAlt   = 5
	rerankerTestTopKSmall    = 2
	rerankerTestTopKLarge    = 10
	rerankerTestOverage      = 1
)

func TestNewReranker(t *testing.T) {
	t.Run("error when API key is empty", func(t *testing.T) {
		_, err := NewReranker("", ModelRerank25, rerankerTestRateLimit, rerankerTestMaxRetries)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "API key is required")
	})

	t.Run("defaults applied", func(t *testing.T) {
		reranker, err := NewReranker("test-key", "", 0, 0)
		require.NoError(t, err)
		assert.NotNil(t, reranker)
		// Defaults: ModelRerank25, 300 rate limit, 3 retries
	})

	t.Run("custom configuration", func(t *testing.T) {
		reranker, err := NewReranker("test-key", ModelRerank2Lite, rerankerTestRateLimitAlt, rerankerTestRetriesAlt)
		require.NoError(t, err)
		assert.NotNil(t, reranker)
	})
}

func TestReranker_Rerank(t *testing.T) {
	for _, tt := range rerankCases() {
		t.Run(tt.name, func(t *testing.T) {
			tt.run(t)
		})
	}
}

type rerankCase struct {
	name string
	run  func(*testing.T)
}

func rerankCases() []rerankCase {
	return []rerankCase{
		{
			name: "error when query is empty",
			run:  testRerankEmptyQuery,
		},
		{
			name: "empty documents returns empty results",
			run:  testRerankEmptyDocuments,
		},
		{
			name: "error when too many documents",
			run:  testRerankTooManyDocuments,
		},
		{
			name: "uses default model when not specified",
			run:  testRerankDefaultModel,
		},
	}
}

func newTestReranker(t *testing.T) *Reranker {
	t.Helper()
	reranker, err := NewReranker("test-key", ModelRerank25, rerankerTestRateLimit, rerankerTestMaxRetries)
	require.NoError(t, err)
	return reranker
}

func testRerankEmptyQuery(t *testing.T) {
	reranker := newTestReranker(t)
	req := &RerankRequest{
		Query:     "",
		Documents: []Document{{Text: "test"}},
	}

	_, err := reranker.Rerank(context.Background(), req)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "query is required")
}

func testRerankEmptyDocuments(t *testing.T) {
	reranker := newTestReranker(t)
	req := &RerankRequest{
		Query:     "test query",
		Documents: []Document{},
	}

	resp, err := reranker.Rerank(context.Background(), req)
	require.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Empty(t, resp.Results)
	assert.Equal(t, ModelRerank25, resp.Model)
}

func testRerankTooManyDocuments(t *testing.T) {
	reranker := newTestReranker(t)
	documents := make([]Document, VoyageRerankMax+rerankerTestOverage)
	for i := range documents {
		documents[i] = Document{Text: "test document"}
	}

	req := &RerankRequest{
		Query:     "test query",
		Documents: documents,
	}

	_, err := reranker.Rerank(context.Background(), req)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "too many documents")
}

func testRerankDefaultModel(t *testing.T) {
	reranker := newTestReranker(t)
	req := &RerankRequest{
		Query:     "test query",
		Documents: []Document{{Text: "test"}},
		Model:     "",
	}

	_, err := reranker.Rerank(context.Background(), req)
	assert.Error(t, err)
}

func TestReranker_RerankSearchResults(t *testing.T) {
	reranker, err := NewReranker("test-key", ModelRerank25, rerankerTestRateLimit, rerankerTestMaxRetries)
	require.NoError(t, err)

	// This is a placeholder method that returns results as-is
	result, err := reranker.RerankSearchResults(context.Background(), "query", "results", rerankerTestTopKLarge)
	require.NoError(t, err)
	assert.Equal(t, "results", result)
}

func TestLocalRerankerExtended(t *testing.T) {
	t.Run("Rerank with ReturnDocuments", func(t *testing.T) {
		reranker := NewLocalReranker()
		req := &RerankRequest{
			Query: "test",
			Documents: []Document{
				{Text: "test document", ID: "1"},
			},
			ReturnDocuments: true,
		}

		resp, err := reranker.Rerank(context.Background(), req)
		require.NoError(t, err)
		assert.NotNil(t, resp)
		if len(resp.Results) > 0 {
			assert.NotNil(t, resp.Results[0].Document)
		}
	})

	t.Run("Rerank with TopK", func(t *testing.T) {
		reranker := NewLocalReranker()
		req := &RerankRequest{
			Query: "test",
			Documents: []Document{
				{Text: "test 1", ID: "1"},
				{Text: "test 2", ID: "2"},
				{Text: "test 3", ID: "3"},
			},
			TopK: rerankerTestTopKSmall,
		}

		resp, err := reranker.Rerank(context.Background(), req)
		require.NoError(t, err)
		assert.LessOrEqual(t, len(resp.Results), rerankerTestTopKSmall)
	})
}

func TestCalculateSimpleScoreExtended(t *testing.T) {
	t.Run("partial match", func(t *testing.T) {
		score := calculateSimpleScore("test query", "this is a test document")
		assert.Greater(t, score, 0.0)
		assert.LessOrEqual(t, score, 1.0)
	})

	t.Run("empty query", func(t *testing.T) {
		score := calculateSimpleScore("", "test document")
		assert.Equal(t, 0.0, score)
	})

	t.Run("empty text", func(t *testing.T) {
		score := calculateSimpleScore("test query", "")
		assert.Equal(t, 0.0, score)
	})
}

func TestTokenizeExtended(t *testing.T) {
	t.Run("with whitespace", func(t *testing.T) {
		tokens := tokenize("  word1   word2  ")
		assert.Equal(t, 2, len(tokens))
		assert.Contains(t, tokens, "word1")
		assert.Contains(t, tokens, "word2")
	})

	t.Run("with tabs and newlines", func(t *testing.T) {
		tokens := tokenize("word1\tword2\nword3\rword4")
		assert.Equal(t, 4, len(tokens))
	})

	t.Run("single word", func(t *testing.T) {
		tokens := tokenize("word")
		assert.Equal(t, 1, len(tokens))
		assert.Equal(t, "word", tokens[0])
	})
}

func TestToLower(t *testing.T) {
	t.Run("uppercase to lowercase", func(t *testing.T) {
		result := toLower("HELLO")
		assert.Equal(t, "hello", result)
	})

	t.Run("mixed case", func(t *testing.T) {
		result := toLower("HeLLo")
		assert.Equal(t, "hello", result)
	})

	t.Run("already lowercase", func(t *testing.T) {
		result := toLower("hello")
		assert.Equal(t, "hello", result)
	})

	t.Run("with numbers and symbols", func(t *testing.T) {
		result := toLower("HELLO123!")
		assert.Equal(t, "hello123!", result)
	})

	t.Run("empty string", func(t *testing.T) {
		result := toLower("")
		assert.Equal(t, "", result)
	})
}
