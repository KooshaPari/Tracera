# Supabase Complete Setup Guide

## Already Configured ✅

Supabase is already set up from Phase 2:
- ✅ Project created: "TraceRTM"
- ✅ Reference ID: uftgquyagdvshekivcat
- ✅ Region: East US
- ✅ Schema deployed with 8 tables
- ✅ Indexes created
- ✅ Foreign keys configured

## Environment Variables

```bash
# From Supabase Dashboard
SUPABASE_URL=https://uftgquyagdvshekivcat.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:password@db.uftgquyagdvshekivcat.supabase.co:5432/postgres
```

## Go Integration (Already Done)

```go
// backend/internal/database/database.go
import (
    "github.com/jackc/pgx/v5/pgxpool"
)

func NewPool(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(databaseURL)
    if err != nil {
        return nil, err
    }
    
    pool, err := pgxpool.NewWithConfig(ctx, config)
    if err != nil {
        return nil, err
    }
    
    return pool, nil
}
```

## RLS Policies (Row Level Security)

### 1. Enable RLS on All Tables
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE links ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
```

### 2. Create Policies

```sql
-- Profiles: Users can only see their own profile
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = user_id);

-- Projects: Users can see projects they own
CREATE POLICY "Users can view own projects"
ON projects FOR SELECT
USING (auth.uid() = owner_id);

-- Items: Users can see items in their projects
CREATE POLICY "Users can view items in own projects"
ON items FOR SELECT
USING (
    project_id IN (
        SELECT id FROM projects WHERE owner_id = auth.uid()
    )
);
```

## Real-Time Subscriptions

### 1. Enable Real-Time
```sql
-- Enable real-time for items table
ALTER PUBLICATION supabase_realtime ADD TABLE items;
```

### 2. Go Integration

```go
// backend/internal/realtime/client.go
import "github.com/supabase-community/supabase-go"

type RealtimeClient struct {
    client *supabase.Client
}

func NewRealtimeClient(url, key string) *RealtimeClient {
    client := supabase.CreateClient(url, key)
    return &RealtimeClient{client: client}
}

func (r *RealtimeClient) SubscribeToItems() {
    r.client.Realtime.On("*", "items", func(payload *realtime.RealtimeMessagePayload) {
        // Handle real-time updates
    }).Subscribe()
}
```

## Backups

### 1. Automatic Backups
- Supabase automatically backs up daily
- Retention: 7 days (free tier)
- Access via Dashboard → Backups

### 2. Manual Backups
```bash
# Export database
pg_dump postgresql://user:password@host:5432/postgres > backup.sql

# Restore database
psql postgresql://user:password@host:5432/postgres < backup.sql
```

## Performance Optimization

### 1. Indexes (Already Created)
```sql
-- Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'items';
```

### 2. Query Optimization
```go
// Use prepared statements
stmt, _ := pool.Prepare(ctx, "get_items", "SELECT * FROM items WHERE project_id = $1")
rows, _ := pool.Query(ctx, stmt, projectID)
```

### 3. Connection Pooling
```go
config, _ := pgxpool.ParseConfig(databaseURL)
config.MaxConns = 20
config.MinConns = 5
pool, _ := pgxpool.NewWithConfig(ctx, config)
```

## Monitoring

### 1. Supabase Dashboard
- Database size
- Query performance
- Connection count
- Error rates

### 2. PostgreSQL Logs
```sql
-- View recent logs
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

## Security

### 1. API Keys
- **Anon Key**: Public, use in frontend
- **Service Role Key**: Private, use in backend only

### 2. Environment Variables
```bash
# .env.local (never commit)
SUPABASE_URL=https://...
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://...
```

### 3. RLS Policies
- Always enable RLS
- Create restrictive policies
- Test policies thoroughly

## Troubleshooting

### Connection Issues
```bash
# Test connection
psql postgresql://user:password@host:5432/postgres

# Check connection limits
SELECT count(*) FROM pg_stat_activity;
```

### Query Issues
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = $1;
```

## Cost

- **Free Tier**:
  - 500MB database
  - 2GB bandwidth
  - Perfect for development
- **Pro Tier**: $25/month
  - 8GB database
  - 50GB bandwidth

## Next Steps

1. ✅ Supabase already configured
2. Enable RLS policies
3. Set up real-time subscriptions
4. Configure backups
5. Monitor performance
6. Scale to Pro tier if needed

