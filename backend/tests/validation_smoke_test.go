package tests

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/tests/testutil"
)

// TestPhase7_IntegrationSmokeTests runs quick integration checks
func TestPhase7_IntegrationSmokeTests(t *testing.T) {
	ctx := context.Background()

	pgContainer, connString, err := testutil.PostgresContainer(ctx)
	require.NoError(t, err)
	defer pgContainer.Terminate(ctx)

	dragonflyContainer, redisAddr, err := testutil.DragonflyContainer(ctx)
	require.NoError(t, err)
	defer dragonflyContainer.Terminate(ctx)

	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)
	defer pool.Close()

	err = testutil.ExecuteMigrations(ctx, pool, "../schema.sql")
	require.NoError(t, err)

	gormDB, err := gorm.Open(postgres.Open(connString), &gorm.Config{})
	require.NoError(t, err)

	redisClient := redis.NewClient(&redis.Options{Addr: redisAddr})
	defer redisClient.Close()

	redisCache, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:      "redis://" + redisAddr,
		DefaultTTL:    5 * time.Minute,
		EnableMetrics: true,
	})
	require.NoError(t, err)

	t.Run("create_and_retrieve_project", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			nil,
			nil,
			nil,
		)
		require.NoError(t, err)

		e := echo.New()
		handler := handlers.NewProjectHandler(
			redisCache,
			nil,
			nil,
			nil,
			&testutil.MockBinder{},
			container.ProjectService(),
		)

		reqBody := `{"name":"Smoke Test Project","description":"Test"}`
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", strings.NewReader(reqBody))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err = handler.CreateProject(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusCreated, rec.Code)

		var createdProject map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &createdProject)
		require.NoError(t, err)

		projectID, ok := createdProject["id"].(map[string]interface{})
		require.True(t, ok, "should have project ID")

		idBytes, _ := json.Marshal(projectID)
		var idStr string
		json.Unmarshal(idBytes, &idStr)

		req2 := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+idStr, nil)
		rec2 := httptest.NewRecorder()
		c2 := e.NewContext(req2, rec2)
		c2.SetParamNames("id")
		c2.SetParamValues(idStr)

		err = handler.GetProject(c2)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec2.Code)
	})

	t.Run("cache_integration", func(t *testing.T) {
		err := redisCache.Set(ctx, "test:key", "test-value")
		require.NoError(t, err)

		var value string
		err = redisCache.Get(ctx, "test:key", &value)
		require.NoError(t, err)
		assert.Equal(t, "test-value", value)

		err = redisCache.Delete(ctx, "test:key")
		require.NoError(t, err)
	})

	t.Run("transaction_support", func(t *testing.T) {
		container, err := services.NewServiceContainer(
			gormDB,
			redisClient,
			redisCache,
			nil,
			nil,
			nil,
		)
		require.NoError(t, err)

		err = container.WithTx(ctx, func(txCtx context.Context) error {
			return nil
		})
		require.NoError(t, err)

		err = container.WithTx(ctx, func(txCtx context.Context) error {
			return assert.AnError
		})
		require.Error(t, err, "should rollback on error")
	})
}
