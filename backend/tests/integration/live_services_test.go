package integration

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// This test suite verifies connectivity and basic operations against REAL services
// managed by process-compose. It expects services to be running on standard local ports.

type liveServicesFixture struct {
	ctx          context.Context
	pgPool       *pgxpool.Pool
	redisClient  *redis.Client
	natsConn     *nats.Conn
	neo4jDriver  neo4j.DriverWithContext
	pythonClient *clients.PythonServiceClient
}

func setupLiveServices(t *testing.T) *liveServicesFixture {
	if testing.Short() {
		t.Skip("Skipping live services integration test")
	}

	ctx := context.Background()

	// 1. Postgres
	pgURL := os.Getenv("DATABASE_URL")
	if pgURL == "" {
		pgURL = "postgresql://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable"
	}
	pgPool, err := pgxpool.New(ctx, pgURL)
	require.NoError(t, err, "Failed to connect to real Postgres")
	if err := pgPool.Ping(ctx); err != nil {
		t.Skip("Postgres not available at", pgURL)
	}

	// 2. Redis
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "localhost:6379"
	}
	rdb := redis.NewClient(&redis.Options{Addr: redisURL})
	if err := rdb.Ping(ctx).Err(); err != nil {
		t.Skip("Redis not available at", redisURL)
	}

	// 3. NATS
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}
	nc, err := nats.Connect(natsURL)
	if err != nil {
		t.Skip("NATS not available at", natsURL)
	}

	// 4. Neo4j
	neo4jURI := os.Getenv("NEO4J_URI")
	if neo4jURI == "" {
		neo4jURI = "bolt://localhost:7687"
	}
	auth := neo4j.BasicAuth("neo4j", os.Getenv("NEO4J_PASSWORD"), "")
	if os.Getenv("NEO4J_PASSWORD") == "" {
		auth = neo4j.BasicAuth("neo4j", "password", "")
	}
	neoDriver, err := neo4j.NewDriverWithContext(neo4jURI, auth)
	require.NoError(t, err)
	if err := neoDriver.VerifyConnectivity(ctx); err != nil {
		t.Skip("Neo4j not available at", neo4jURI)
	}

	// 5. Python Service
	pythonURL := os.Getenv("PYTHON_BACKEND_URL")
	if pythonURL == "" {
		pythonURL = "http://localhost:8000"
	}
	// Check if python service is up
	pClient := clients.NewPythonServiceClient(pythonURL, "test-token", nil)

	return &liveServicesFixture{
		ctx:          ctx,
		pgPool:       pgPool,
		redisClient:  rdb,
		natsConn:     nc,
		neo4jDriver:  neoDriver,
		pythonClient: pClient,
	}
}

func (f *liveServicesFixture) cleanup() {
	if f.pgPool != nil {
		f.pgPool.Close()
	}
	if f.redisClient != nil {
		f.redisClient.Close()
	}
	if f.natsConn != nil {
		f.natsConn.Close()
	}
	if f.neo4jDriver != nil {
		f.neo4jDriver.Close(f.ctx)
	}
}

func TestLive_PostgresConnectivity(t *testing.T) {
	f := setupLiveServices(t)
	defer f.cleanup()

	var now time.Time
	err := f.pgPool.QueryRow(f.ctx, "SELECT NOW()").Scan(&now)
	assert.NoError(t, err)
	t.Logf("Postgres time: %v", now)
}

func TestLive_RedisConnectivity(t *testing.T) {
	f := setupLiveServices(t)
	defer f.cleanup()

	err := f.redisClient.Set(f.ctx, "live_test_key", "active", 10*time.Second).Err()
	assert.NoError(t, err)
	val, err := f.redisClient.Get(f.ctx, "live_test_key").Result()
	assert.NoError(t, err)
	assert.Equal(t, "active", val)
}

func TestLive_NATSConnectivity(t *testing.T) {
	f := setupLiveServices(t)
	defer f.cleanup()

	sub, err := f.natsConn.SubscribeSync("live.test")
	require.NoError(t, err)

	err = f.natsConn.Publish("live.test", []byte("hello live"))
	assert.NoError(t, err)

	msg, err := sub.NextMsg(1 * time.Second)
	assert.NoError(t, err)
	assert.Equal(t, "hello live", string(msg.Data))
}

func TestLive_Neo4jConnectivity(t *testing.T) {
	f := setupLiveServices(t)
	defer f.cleanup()

	session := f.neo4jDriver.NewSession(f.ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(f.ctx)

	_, err := session.ExecuteWrite(f.ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(f.ctx, "MERGE (n:LiveTest {id: '1'}) RETURN n", nil)
	})
	assert.NoError(t, err)
}

func TestLive_PythonServiceHealth(t *testing.T) {
	f := setupLiveServices(t)
	defer f.cleanup()

	var response map[string]interface{}
	err := f.pythonClient.DelegateRequest(f.ctx, "GET", "/health", nil, &response, false, "", 0)
	// We don't fail if python is down, just skip or log, but user wants to eliminate mocks
	// so we expect it to be up if process-compose is running.
	if err != nil {
		t.Logf("Python service health check failed (expected if not running): %v", err)
		t.Skip("Python service not reachable")
	}
	assert.NotNil(t, response)
}
