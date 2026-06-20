# Search Service - Usage Examples

## Table of Contents
1. [Setup](#setup)
2. [Full-Text Search](#full-text-search)
3. [Semantic Search](#semantic-search)
4. [Hybrid Search](#hybrid-search)
5. [Fuzzy Search](#fuzzy-search)
6. [Advanced Filtering](#advanced-filtering)
7. [Autocomplete](#autocomplete)
8. [Indexing](#indexing)
9. [Performance Tuning](#performance-tuning)

## Setup

### Initialize Search Service

```go
package main

import (
    "context"
    "log"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/kooshapari/tracertm-backend/internal/cache"
    "github.com/kooshapari/tracertm-backend/internal/embeddings"
    "github.com/kooshapari/tracertm-backend/internal/search"
)

func main() {
    // Initialize database connection
    dbURL := "postgres://user:pass@localhost:5432/tracertm"
    pool, err := pgxpool.New(context.Background(), dbURL)
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()

    // Initialize Redis cache
    redisCache, err := cache.NewRedisCache("redis://localhost:6379", 5*time.Minute)
    if err != nil {
        log.Fatal(err)
    }
    defer redisCache.Close()

    // Initialize embedding provider (optional, for semantic search)
    provider := embeddings.NewVoyageProvider("your-api-key")
    reranker := embeddings.NewReranker(provider)

    // Create search service with all features
    service := search.NewServiceWithEmbeddings(pool, redisCache, provider, reranker)

    // Or create basic service (without semantic search)
    // service := search.NewService(pool, redisCache)
}
```

## Full-Text Search

### Basic Keyword Search

```go
func basicSearch(ctx context.Context, service *search.Service) {
    results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "authentication",
        Limit: 20,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    fmt.Printf("Found %d results in %v\n", results.Total, results.TimeTaken)
    for _, result := range results.Results {
        fmt.Printf("- %s (score: %.2f)\n", result.Title, result.Score)
    }
}
```

### Search with Project Filter

```go
func projectSearch(ctx context.Context, service *search.Service, projectID string) {
    results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query:     "user login",
        ProjectID: projectID,
        Limit:     20,
        MinScore:  0.2, // Filter low-relevance results
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    for _, result := range results.Results {
        fmt.Printf("ID: %s\n", result.ItemID)
        fmt.Printf("Title: %s\n", result.Title)
        fmt.Printf("Type: %s\n", result.Type)
        fmt.Printf("Score: %.2f\n\n", result.Score)
    }
}
```

### Search with Type Filter

```go
func typeFilteredSearch(ctx context.Context, service *search.Service) {
    results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "payment processing",
        Types: []string{"requirement", "feature"}, // Only these types
        Limit: 20,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    // Group by type
    byType := make(map[string][]search.SearchResult)
    for _, result := range results.Results {
        byType[result.Type] = append(byType[result.Type], result)
    }

    for typ, items := range byType {
        fmt.Printf("%s (%d):\n", typ, len(items))
        for _, item := range items {
            fmt.Printf("  - %s\n", item.Title)
        }
    }
}
```

### Boolean Search

```go
func booleanSearch(ctx context.Context, service *search.Service) {
    // AND operator
    results, _ := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "authentication AND login",
    })

    // OR operator
    results, _ = service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "authentication OR authorization",
    })

    // NOT operator
    results, _ = service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "authentication NOT password",
    })

    // Complex boolean
    results, _ = service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "(authentication OR login) AND (oauth OR saml)",
    })
}
```

### Paginated Search

```go
func paginatedSearch(ctx context.Context, service *search.Service) {
    pageSize := 20
    page := 0

    for {
        results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
            Query:  "requirement",
            Limit:  pageSize,
            Offset: page * pageSize,
        })

        if err != nil {
            log.Printf("Search failed: %v", err)
            break
        }

        if len(results.Results) == 0 {
            break // No more results
        }

        fmt.Printf("Page %d:\n", page+1)
        for _, result := range results.Results {
            fmt.Printf("  - %s\n", result.Title)
        }

        page++

        if len(results.Results) < pageSize {
            break // Last page
        }
    }
}
```

## Semantic Search

### Basic Semantic Search

```go
func semanticSearch(ctx context.Context, service *search.Service) {
    results, err := service.SemanticSearch(ctx, search.SemanticSearchRequest{
        Query:     "how do users authenticate",
        TopK:      20,
        Threshold: 0.5, // Minimum similarity
    })

    if err != nil {
        log.Printf("Semantic search failed: %v", err)
        return
    }

    fmt.Printf("Found %d semantically similar results\n", len(results.Results))
    for _, result := range results.Results {
        fmt.Printf("- %s (similarity: %.2f)\n", result.Title, result.Score)
    }
}
```

### Cross-Language Search (with embeddings)

```go
func crossLanguageSearch(ctx context.Context, service *search.Service) {
    // Search in English, find results in any language
    results, err := service.SemanticSearch(ctx, search.SemanticSearchRequest{
        Query:     "user authentication system",
        TopK:      10,
        Threshold: 0.6,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    // Will find semantically similar items regardless of language
    for _, result := range results.Results {
        fmt.Printf("%s: %s (%.2f)\n", result.Type, result.Title, result.Score)
    }
}
```

### Find Similar Items

```go
func findSimilarItems(ctx context.Context, service *search.Service, itemTitle string) {
    // Use the item title as the query to find similar items
    results, err := service.SemanticSearch(ctx, search.SemanticSearchRequest{
        Query:     itemTitle,
        TopK:      5,
        Threshold: 0.7, // Higher threshold for better matches
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    fmt.Printf("Items similar to '%s':\n", itemTitle)
    for i, result := range results.Results {
        fmt.Printf("%d. %s (%.1f%% similar)\n",
            i+1, result.Title, result.Score*100)
    }
}
```

## Hybrid Search

### Balanced Hybrid Search

```go
func hybridSearch(ctx context.Context, service *search.Service) {
    results, err := service.HybridSearch(ctx, search.HybridSearchRequest{
        Query:          "authentication system",
        Limit:          20,
        TextWeight:     0.5, // 50% keyword matching
        SemanticWeight: 0.5, // 50% semantic similarity
    })

    if err != nil {
        log.Printf("Hybrid search failed: %v", err)
        return
    }

    fmt.Printf("Hybrid search results (%d):\n", len(results.Results))
    for _, result := range results.Results {
        fmt.Printf("- %s (combined score: %.2f)\n", result.Title, result.Score)
    }
}
```

### Keyword-Focused Hybrid Search

```go
func keywordFocusedHybrid(ctx context.Context, service *search.Service) {
    // When you want exact matches but with semantic fallback
    results, err := service.HybridSearch(ctx, search.HybridSearchRequest{
        Query:          "OAuth2 implementation",
        Limit:          20,
        TextWeight:     0.8, // 80% keyword matching
        SemanticWeight: 0.2, // 20% semantic similarity
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    for _, result := range results.Results {
        fmt.Printf("%s: %s (%.2f)\n", result.Type, result.Title, result.Score)
    }
}
```

### Semantic-Focused Hybrid Search

```go
func semanticFocusedHybrid(ctx context.Context, service *search.Service) {
    // When you want conceptual understanding with keyword boost
    results, err := service.HybridSearch(ctx, search.HybridSearchRequest{
        Query:          "secure user access control",
        Limit:          20,
        TextWeight:     0.3, // 30% keyword matching
        SemanticWeight: 0.7, // 70% semantic similarity
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    for _, result := range results.Results {
        fmt.Printf("%s (%.2f): %s\n", result.Type, result.Score, result.Title)
    }
}
```

## Fuzzy Search

### Typo-Tolerant Search

```go
func fuzzySearch(ctx context.Context, service *search.Service) {
    // Will match "authentication" even with typos
    queries := []string{
        "authenticaton",  // missing 'i'
        "authetication",  // transposed letters
        "authentification", // extra letter
    }

    for _, query := range queries {
        results, err := service.FuzzySearch(ctx, search.FuzzySearchRequest{
            Query:       query,
            MaxDistance: 3, // Allow up to 3 character differences
            Limit:       5,
        })

        if err != nil {
            log.Printf("Fuzzy search failed: %v", err)
            continue
        }

        fmt.Printf("Query: %s\n", query)
        for _, result := range results.Results {
            fmt.Printf("  - %s (similarity: %.2f)\n", result.Title, result.Score)
        }
        fmt.Println()
    }
}
```

### Partial Match Search

```go
func partialMatchSearch(ctx context.Context, service *search.Service) {
    // Find items with partial matches
    results, err := service.FuzzySearch(ctx, search.FuzzySearchRequest{
        Query:       "auth",
        MaxDistance: 2,
        Limit:       10,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    // Will find "authentication", "authorization", "oauth", etc.
    for _, result := range results.Results {
        fmt.Printf("%s (%.1f%% match)\n", result.Title, result.Score*100)
    }
}
```

## Advanced Filtering

### Complex Filter Example

```go
func advancedFilterSearch(ctx context.Context, service *search.Service) {
    results, err := service.AdvancedSearch(ctx, search.AdvancedSearchRequest{
        ProjectID: "proj-123",
        Query:     "authentication",
        Filters: []search.SearchFilter{
            {
                Field:    "type",
                Operator: "eq",
                Value:    "requirement",
            },
            {
                Field:    "status",
                Operator: "in",
                Value:    []string{"active", "review", "approved"},
            },
            {
                Field:    "priority",
                Operator: "gt",
                Value:    5,
            },
        },
        Sort: []search.SortOption{
            {Field: "priority", Direction: "desc"},
            {Field: "updated_at", Direction: "desc"},
        },
        Limit:  20,
        Offset: 0,
    })

    if err != nil {
        log.Printf("Advanced search failed: %v", err)
        return
    }

    for _, result := range results.Results {
        fmt.Printf("[%s] %s - Priority: %s\n",
            result.Type, result.Title, result.Metadata["priority"])
    }
}
```

### Date Range Filter

```go
func dateRangeSearch(ctx context.Context, service *search.Service) {
    results, err := service.AdvancedSearch(ctx, search.AdvancedSearchRequest{
        Query: "requirement",
        Filters: []search.SearchFilter{
            {
                Field:    "created_at",
                Operator: "gt",
                Value:    "2024-01-01",
            },
            {
                Field:    "created_at",
                Operator: "lt",
                Value:    "2024-12-31",
            },
        },
        Sort: []search.SortOption{
            {Field: "created_at", Direction: "desc"},
        },
        Limit: 50,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    fmt.Printf("Found %d items created in 2024\n", len(results.Results))
}
```

### Multi-Field Search

```go
func multiFieldSearch(ctx context.Context, service *search.Service) {
    results, err := service.AdvancedSearch(ctx, search.AdvancedSearchRequest{
        Query: "payment",
        Filters: []search.SearchFilter{
            {
                Field:    "type",
                Operator: "in",
                Value:    []string{"requirement", "feature", "epic"},
            },
            {
                Field:    "status",
                Operator: "neq",
                Value:    "archived",
            },
            {
                Field:    "title",
                Operator: "contains",
                Value:    "process",
            },
        },
        Limit: 20,
    })

    if err != nil {
        log.Printf("Search failed: %v", err)
        return
    }

    for _, result := range results.Results {
        fmt.Printf("%s: %s\n", result.Type, result.Title)
    }
}
```

## Autocomplete

### Basic Autocomplete

```go
func autocomplete(ctx context.Context, service *search.Service, prefix string) {
    suggestions, err := service.Suggest(ctx, prefix, 10)

    if err != nil {
        log.Printf("Suggest failed: %v", err)
        return
    }

    fmt.Printf("Suggestions for '%s':\n", prefix)
    for i, suggestion := range suggestions {
        fmt.Printf("%d. %s (score: %.2f)\n", i+1, suggestion.Text, suggestion.Score)
    }
}
```

### Real-Time Autocomplete (as user types)

```go
func realtimeAutocomplete(ctx context.Context, service *search.Service) {
    // Simulate user typing
    queries := []string{"a", "au", "aut", "auth"}

    for _, query := range queries {
        if len(query) < 2 {
            continue // Don't search for single characters
        }

        suggestions, err := service.Suggest(ctx, query, 5)
        if err != nil {
            continue
        }

        fmt.Printf("Typing '%s':\n", query)
        for _, s := range suggestions {
            fmt.Printf("  - %s\n", s.Text)
        }
        fmt.Println()
    }
}
```

## Indexing

### Index Single Item

```go
func indexItem(ctx context.Context, service *search.Service) {
    item := &search.Item{
        ID:          "item-123",
        Title:       "User Authentication Flow",
        Description: "Implement OAuth2 authentication with JWT tokens",
        Type:        "requirement",
        Metadata: map[string]interface{}{
            "priority": 8,
            "status":   "active",
        },
        ProjectID: "proj-123",
    }

    err := service.IndexItem(ctx, item)
    if err != nil {
        log.Printf("Indexing failed: %v", err)
        return
    }

    fmt.Println("Item indexed successfully")
}
```

### Batch Index Items

```go
func batchIndexItems(ctx context.Context, service *search.Service) {
    items := []*search.Item{
        {
            ID:          "item-1",
            Title:       "Login Form",
            Description: "Create user login form with validation",
            Type:        "feature",
        },
        {
            ID:          "item-2",
            Title:       "Password Reset",
            Description: "Implement password reset functionality",
            Type:        "feature",
        },
        {
            ID:          "item-3",
            Title:       "Two-Factor Auth",
            Description: "Add 2FA support via TOTP",
            Type:        "feature",
        },
    }

    err := service.BatchIndexItems(ctx, items)
    if err != nil {
        log.Printf("Batch indexing failed: %v", err)
        return
    }

    fmt.Printf("Indexed %d items successfully\n", len(items))
}
```

### Re-index After Update

```go
func updateAndReindex(ctx context.Context, service *search.Service, itemID string) {
    // 1. Update item in database
    // updateItemInDB(itemID, newData)

    // 2. Re-index for search
    item := &search.Item{
        ID:          itemID,
        Title:       "Updated Title",
        Description: "Updated description",
        Type:        "requirement",
    }

    err := service.IndexItem(ctx, item)
    if err != nil {
        log.Printf("Re-indexing failed: %v", err)
        return
    }

    fmt.Println("Item re-indexed successfully")
}
```

### Delete from Index

```go
func deleteFromIndex(ctx context.Context, service *search.Service, itemID string) {
    err := service.DeleteFromIndex(ctx, itemID)
    if err != nil {
        log.Printf("Delete from index failed: %v", err)
        return
    }

    fmt.Println("Item removed from search index")
}
```

## Performance Tuning

### Measure Search Performance

```go
func measurePerformance(ctx context.Context, service *search.Service) {
    queries := []string{
        "authentication",
        "user login flow",
        "payment processing",
    }

    for _, query := range queries {
        start := time.Now()

        results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
            Query: query,
            Limit: 20,
        })

        duration := time.Since(start)

        if err != nil {
            log.Printf("Query failed: %v", err)
            continue
        }

        fmt.Printf("Query: %s\n", query)
        fmt.Printf("  Results: %d\n", len(results.Results))
        fmt.Printf("  Time: %v\n", duration)
        fmt.Printf("  From cache: %v\n", results.FromCache)
        fmt.Println()
    }
}
```

### Optimize with Appropriate Limits

```go
func optimizedSearch(ctx context.Context, service *search.Service) {
    // Good: Reasonable limit
    results, _ := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "requirement",
        Limit: 20, // Just what we need
    })

    // Bad: Too large (will be capped at 100 anyway)
    results, _ = service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "requirement",
        Limit: 1000, // Unnecessary
    })

    // Good: Paginate for large result sets
    pageSize := 20
    for page := 0; page < 5; page++ {
        results, _ = service.FullTextSearch(ctx, search.FullTextSearchRequest{
            Query:  "requirement",
            Limit:  pageSize,
            Offset: page * pageSize,
        })

        if len(results.Results) < pageSize {
            break // Last page
        }
    }
}
```

### Cache Warming

```go
func warmCache(ctx context.Context, service *search.Service) {
    // Pre-load common searches into cache
    commonQueries := []string{
        "authentication",
        "authorization",
        "payment",
        "user",
        "api",
    }

    for _, query := range commonQueries {
        _, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
            Query: query,
            Limit: 20,
        })

        if err != nil {
            log.Printf("Cache warming failed for '%s': %v", query, err)
        }
    }

    fmt.Println("Cache warmed successfully")
}
```

## Error Handling

### Robust Error Handling

```go
func robustSearch(ctx context.Context, service *search.Service) {
    results, err := service.FullTextSearch(ctx, search.FullTextSearchRequest{
        Query: "authentication",
        Limit: 20,
    })

    if err != nil {
        // Log error
        log.Printf("Search error: %v", err)

        // Return empty results gracefully
        results = &search.SearchResults{
            Query:   "authentication",
            Results: []search.SearchResult{},
            Total:   0,
        }
    }

    // Always safe to use results
    fmt.Printf("Found %d results\n", len(results.Results))
}
```

### Fallback Strategy

```go
func searchWithFallback(ctx context.Context, service *search.Service, query string) {
    // Try semantic search first
    results, err := service.SemanticSearch(ctx, search.SemanticSearchRequest{
        Query:     query,
        TopK:      20,
        Threshold: 0.5,
    })

    if err != nil || len(results.Results) == 0 {
        // Fall back to full-text search
        results, err = service.FullTextSearch(ctx, search.FullTextSearchRequest{
            Query: query,
            Limit: 20,
        })

        if err != nil {
            log.Printf("Both searches failed: %v", err)
            return
        }
    }

    // Use results
    for _, result := range results.Results {
        fmt.Printf("%s: %s\n", result.Type, result.Title)
    }
}
```
