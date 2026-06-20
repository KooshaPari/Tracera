package database

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// Standalone tests that don't require other package imports
// These can be compiled and run independently

func TestDefaultOptimizationConfigStandalone(t *testing.T) {
	t.Run("returns valid configuration", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.NotNil(t, config)
		assert.Equal(t, int32(25), config.MaxConnections)
		assert.Equal(t, int32(5), config.MinConnections)
		assert.Equal(t, 1*time.Hour, config.MaxConnLifetime)
		assert.Equal(t, 30*time.Minute, config.MaxConnIdleTime)
		assert.Equal(t, 1*time.Minute, config.HealthCheckPeriod)
		assert.Equal(t, 30*time.Second, config.StatementTimeout)
		assert.Equal(t, 5*time.Minute, config.IdleInTxTimeout)
		assert.True(t, config.PreparedStatements)
	})

	t.Run("config is not nil", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.NotNil(t, config)
	})

	t.Run("config values are positive", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.Positive(t, config.MaxConnections)
		assert.Positive(t, config.MinConnections)
		assert.Greater(t, config.MaxConnLifetime, time.Duration(0))
		assert.Greater(t, config.MaxConnIdleTime, time.Duration(0))
		assert.Greater(t, config.HealthCheckPeriod, time.Duration(0))
		assert.Greater(t, config.StatementTimeout, time.Duration(0))
		assert.Greater(t, config.IdleInTxTimeout, time.Duration(0))
	})

	t.Run("max connections >= min connections", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.GreaterOrEqual(t, config.MaxConnections, config.MinConnections)
	})

	t.Run("prepared statements enabled", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		assert.True(t, config.PreparedStatements)
	})
}

func TestOptimizationConfigMultipleCalls(t *testing.T) {
	t.Run("multiple calls return different instances", func(t *testing.T) {
		config1 := DefaultOptimizationConfig()
		config2 := DefaultOptimizationConfig()

		// Both should have same values
		assert.Equal(t, config1.MaxConnections, config2.MaxConnections)

		// But they are different objects
		config1.MaxConnections = 100
		assert.NotEqual(t, config1.MaxConnections, config2.MaxConnections)
	})

	t.Run("config can be modified after creation", func(t *testing.T) {
		config := DefaultOptimizationConfig()
		originalMax := config.MaxConnections

		config.MaxConnections = 50
		assert.Equal(t, int32(50), config.MaxConnections)
		assert.NotEqual(t, originalMax, config.MaxConnections)
	})
}

func TestSlowQueryType(t *testing.T) {
	t.Run("SlowQuery can be instantiated", func(t *testing.T) {
		sq := SlowQuery{
			Query:          "SELECT * FROM items",
			Calls:          int64(100),
			TotalExecTime:  5000.0,
			MeanExecTime:   50.0,
			MaxExecTime:    200.0,
			StddevExecTime: 25.0,
		}

		assert.Equal(t, "SELECT * FROM items", sq.Query)
		assert.Equal(t, int64(100), sq.Calls)
		assert.InEpsilon(t, 5000.0, sq.TotalExecTime, 1e-9)
		assert.InEpsilon(t, 50.0, sq.MeanExecTime, 1e-9)
		assert.InEpsilon(t, 200.0, sq.MaxExecTime, 1e-9)
		assert.InEpsilon(t, 25.0, sq.StddevExecTime, 1e-9)
	})

	t.Run("SlowQuery fields are accessible", func(t *testing.T) {
		sq := SlowQuery{}
		sq.Query = "TEST"
		sq.Calls = 42

		assert.Equal(t, "TEST", sq.Query)
		assert.Equal(t, int64(42), sq.Calls)
	})
}

func TestTableStatsType(t *testing.T) {
	t.Run("TableStats can be instantiated", func(t *testing.T) {
		now := time.Now()
		stats := TableStats{
			SchemaName:      "public",
			TableName:       "items",
			Size:            "100MB",
			Inserts:         int64(1000),
			Updates:         int64(500),
			Deletes:         int64(100),
			LiveTuples:      int64(1400),
			DeadTuples:      int64(50),
			LastVacuum:      &now,
			LastAutovacuum:  &now,
			LastAnalyze:     &now,
			LastAutoanalyze: &now,
		}

		assert.Equal(t, "public", stats.SchemaName)
		assert.Equal(t, "items", stats.TableName)
		assert.Equal(t, "100MB", stats.Size)
		assert.Equal(t, int64(1000), stats.Inserts)
		assert.Equal(t, int64(1400), stats.LiveTuples)
		assert.NotNil(t, stats.LastVacuum)
	})

	t.Run("TableStats with nil timestamps", func(t *testing.T) {
		stats := TableStats{
			SchemaName: "public",
			TableName:  "test",
			Size:       "50MB",
			Inserts:    100,
		}

		assert.Nil(t, stats.LastVacuum)
		assert.Nil(t, stats.LastAutovacuum)
		assert.Nil(t, stats.LastAnalyze)
		assert.Nil(t, stats.LastAutoanalyze)
	})

	t.Run("TableStats fields are mutable", func(t *testing.T) {
		stats := TableStats{}
		stats.TableName = "new_table"
		stats.Size = "200MB"
		stats.Inserts = 5000

		assert.Equal(t, "new_table", stats.TableName)
		assert.Equal(t, "200MB", stats.Size)
		assert.Equal(t, int64(5000), stats.Inserts)
	})
}

func BenchmarkDefaultOptimizationConfigStandalone(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = DefaultOptimizationConfig()
	}
}

func BenchmarkSlowQueryCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = SlowQuery{
			Query:          "SELECT * FROM items",
			Calls:          100,
			TotalExecTime:  5000.0,
			MeanExecTime:   50.0,
			MaxExecTime:    200.0,
			StddevExecTime: 25.0,
		}
	}
}

func BenchmarkTableStatsCreation(b *testing.B) {
	now := time.Now()
	for i := 0; i < b.N; i++ {
		_ = TableStats{
			SchemaName:      "public",
			TableName:       "items",
			Size:            "100MB",
			Inserts:         1000,
			Updates:         500,
			Deletes:         100,
			LiveTuples:      1400,
			DeadTuples:      50,
			LastVacuum:      &now,
			LastAutovacuum:  &now,
			LastAnalyze:     &now,
			LastAutoanalyze: &now,
		}
	}
}
