# Algolia vs Meilisearch: Free Tier Comparison

## Quick Comparison

| Feature | Algolia | Meilisearch | Winner |
|---------|---------|-------------|--------|
| **Free Tier** | 10K records | Unlimited | Meilisearch ✅ |
| **Search Speed** | <100ms | <200ms | Algolia ✅ |
| **Typo Tolerance** | Yes | Yes | Tie |
| **Faceting** | Yes | Yes | Tie |
| **Filtering** | Advanced | Basic | Algolia ✅ |
| **Setup** | Cloud only | Self-hosted | Meilisearch ✅ |
| **Cost** | $0/month (free) | $0/month (free) | Tie |
| **Scaling** | $0.10/1K records | $0.50/month | Algolia ✅ |

## Algolia

### Pros ✅
- Fastest search (<100ms)
- Advanced filtering
- Typo tolerance
- Analytics included
- Global CDN
- Excellent documentation

### Cons ❌
- Only 10K records free tier
- Cloud-only (no self-hosted)
- Expensive at scale
- Overkill for small projects

### Free Tier
```
- 10,000 records
- 100,000 operations/month
- 1 index
- Basic analytics
```

### Pricing
```
- Free: 10K records
- Growth: $0.10 per 1,000 records
- Premium: Custom pricing
```

### Go Integration

```go
// backend/internal/search/algolia.go
import "github.com/algolia/algoliasearch-client-go/v3/algolia/search"

type AlgoliaSearch struct {
    client *search.Client
    index  search.Index
}

func NewAlgoliaSearch(appID, apiKey string) *AlgoliaSearch {
    client := search.NewClient(appID, apiKey)
    index := client.InitIndex("items")
    return &AlgoliaSearch{client: client, index: index}
}

func (a *AlgoliaSearch) IndexItem(item Item) error {
    _, err := a.index.SaveObject(item)
    return err
}

func (a *AlgoliaSearch) Search(query string) ([]Item, error) {
    res, err := a.index.Search(query)
    if err != nil {
        return nil, err
    }
    
    var items []Item
    res.UnmarshalHits(&items)
    return items, nil
}
```

## Meilisearch

### Pros ✅
- Unlimited records free tier
- Self-hosted option
- Easy setup (Docker)
- Typo tolerance
- Great for development
- Open source

### Cons ❌
- Slower search (~200ms)
- Basic filtering
- No analytics
- Smaller community
- Self-hosted requires maintenance

### Free Tier
```
- Unlimited records
- Unlimited searches
- Self-hosted or cloud
- Perfect for development
```

### Pricing
```
- Free: Self-hosted (unlimited)
- Cloud Free: Unlimited
- Cloud Pro: $0.50/month
```

### Go Integration

```go
// backend/internal/search/meilisearch.go
import "github.com/meilisearch/meilisearch-go"

type MeilisearchClient struct {
    client *meilisearch.Client
    index  *meilisearch.Index
}

func NewMeilisearch(url, apiKey string) (*MeilisearchClient, error) {
    client := meilisearch.NewClient(meilisearch.ClientConfig{
        Host:   url,
        APIKey: apiKey,
    })
    
    index := client.Index("items")
    return &MeilisearchClient{client: client, index: index}, nil
}

func (m *MeilisearchClient) IndexItem(item Item) error {
    _, err := m.index.AddDocuments(item)
    return err
}

func (m *MeilisearchClient) Search(query string) ([]Item, error) {
    res, err := m.index.Search(query, &meilisearch.SearchRequest{})
    if err != nil {
        return nil, err
    }
    
    var items []Item
    for _, hit := range res.Hits {
        // Parse hit into item
    }
    return items, nil
}
```

## Recommendation: Meilisearch ✅

**Why Meilisearch is best for TraceRTM:**

1. **Unlimited Free Tier**
   - No record limits
   - Perfect for development and testing
   - Scale without worrying about limits

2. **Self-Hosted Option**
   - Full control
   - No vendor lock-in
   - Easy Docker setup

3. **Development-Friendly**
   - Quick setup
   - Great for prototyping
   - Easy to test

4. **Cost-Effective**
   - Free for self-hosted
   - $0.50/month for cloud
   - No per-record charges

5. **Good Enough Performance**
   - ~200ms search time
   - Acceptable for most use cases
   - Can optimize with caching

## Setup Instructions

### Local Development (Docker)

```bash
# Start Meilisearch
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  -v meilisearch_data:/meili_data \
  getmeili/meilisearch:latest

# Test
curl http://localhost:7700/health
```

### Production (Cloud)

```bash
# Sign up at https://cloud.meilisearch.com
# Get API key and URL
export MEILISEARCH_URL="https://..."
export MEILISEARCH_KEY="..."
```

### Go Integration

```go
// backend/main.go
searchClient, err := search.NewMeilisearch(
    os.Getenv("MEILISEARCH_URL"),
    os.Getenv("MEILISEARCH_KEY"),
)
if err != nil {
    log.Fatal("Failed to connect to Meilisearch:", err)
}
```

## Usage in Handlers

```go
func (h *SearchHandler) Search(c echo.Context) error {
    query := c.QueryParam("q")
    
    results, err := h.search.Search(query)
    if err != nil {
        return err
    }
    
    return c.JSON(200, results)
}
```

## Monitoring

### Meilisearch Dashboard
```bash
# Access at http://localhost:7700
# Or cloud dashboard
```

### Metrics
- Search latency
- Indexing speed
- Query count
- Error rates

## Migration Path

1. Start with Meilisearch (free)
2. Use PostgreSQL full-text search as fallback
3. Scale to Algolia if needed
4. Or keep Meilisearch self-hosted

## Cost Summary

| Scenario | Algolia | Meilisearch |
|----------|---------|-------------|
| Development | Free (10K) | Free (unlimited) |
| Production (100K items) | $10/month | Free (self-hosted) |
| Production (1M items) | $100/month | $0.50/month (cloud) |

## Conclusion

**Use Meilisearch for TraceRTM:**
- ✅ Unlimited free tier
- ✅ Self-hosted option
- ✅ Cost-effective
- ✅ Good performance
- ✅ Perfect for development

**Switch to Algolia only if:**
- You need <100ms search times
- You need advanced filtering
- You have budget for premium features

