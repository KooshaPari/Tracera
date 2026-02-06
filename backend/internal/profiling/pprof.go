// Package profiling provides pprof HTTP endpoints and optional metrics/health handlers.
package profiling

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"net/http/pprof"
	"runtime"
	"time"
)

const (
	profilingHTTPTimeout = 30 * time.Second
	gcPauseHistorySize   = 256
	gcPauseIndexOffset   = gcPauseHistorySize - 1
)

// Config configures the profiling server.
type Config struct {
	Enabled          bool
	Port             string
	BlockProfileRate int // nanoseconds
	MutexProfileFrac int // fraction
	EnableMemStats   bool
	EnableGCStats    bool
}

// DefaultConfig returns sensible defaults for profiling.
func DefaultConfig() Config {
	return Config{
		Enabled:          true,
		Port:             "6060",
		BlockProfileRate: 1,
		MutexProfileFrac: 1,
		EnableMemStats:   true,
		EnableGCStats:    true,
	}
}

// Server wraps the pprof HTTP server.
type Server struct {
	config Config
	server *http.Server
	mux    *http.ServeMux
}

// NewProfilingServer creates a new profiling server.
func NewProfilingServer(config Config) *Server {
	mux := http.NewServeMux()

	// Standard pprof handlers
	mux.HandleFunc("/debug/pprof/", pprof.Index)
	mux.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
	mux.HandleFunc("/debug/pprof/profile", pprof.Profile)
	mux.HandleFunc("/debug/pprof/symbol", pprof.Symbol)
	mux.HandleFunc("/debug/pprof/trace", pprof.Trace)

	// Additional profile types
	mux.Handle("/debug/pprof/heap", pprof.Handler("heap"))
	mux.Handle("/debug/pprof/goroutine", pprof.Handler("goroutine"))
	mux.Handle("/debug/pprof/threadcreate", pprof.Handler("threadcreate"))
	mux.Handle("/debug/pprof/block", pprof.Handler("block"))
	mux.Handle("/debug/pprof/mutex", pprof.Handler("mutex"))
	mux.Handle("/debug/pprof/allocs", pprof.Handler("allocs"))

	// Custom metrics endpoints
	mux.HandleFunc("/debug/metrics", metricsHandler)
	mux.HandleFunc("/debug/health", healthHandler)

	server := &http.Server{
		Addr:         ":" + config.Port,
		Handler:      mux,
		ReadTimeout:  profilingHTTPTimeout,
		WriteTimeout: profilingHTTPTimeout,
	}

	return &Server{
		config: config,
		server: server,
		mux:    mux,
	}
}

// Start begins the profiling server
func (ps *Server) Start() error {
	if !ps.config.Enabled {
		log.Println("Profiling server is disabled")
		return nil
	}

	// Configure runtime profiling
	runtime.SetBlockProfileRate(ps.config.BlockProfileRate)
	runtime.SetMutexProfileFraction(ps.config.MutexProfileFrac)

	log.Printf("🔍 Starting profiling server on http://localhost:%s/debug/pprof/", ps.config.Port)
	log.Printf("   CPU Profile:     http://localhost:%s/debug/pprof/profile?seconds=30", ps.config.Port)
	log.Printf("   Heap Profile:    http://localhost:%s/debug/pprof/heap", ps.config.Port)
	log.Printf("   Goroutines:      http://localhost:%s/debug/pprof/goroutine", ps.config.Port)
	log.Printf("   Block Profile:   http://localhost:%s/debug/pprof/block", ps.config.Port)
	log.Printf("   Mutex Profile:   http://localhost:%s/debug/pprof/mutex", ps.config.Port)
	log.Printf("   Metrics:         http://localhost:%s/debug/metrics", ps.config.Port)

	go func() {
		if err := ps.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("Profiling server error: %v", err)
		}
	}()

	return nil
}

// Stop gracefully shuts down the profiling server
func (ps *Server) Stop(ctx context.Context) error {
	if !ps.config.Enabled {
		return nil
	}

	log.Println("Stopping profiling server...")
	return ps.server.Shutdown(ctx)
}

// metricsHandler returns runtime metrics in JSON format
func metricsHandler(w http.ResponseWriter, _ *http.Request) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	writeMetricsResponse(w, &m)
}

func writeMetricsResponse(w http.ResponseWriter, m *runtime.MemStats) {
	w.Header().Set("Content-Type", "application/json")
	if _, err := fmt.Fprintf(w, `{
  "memory": %s,
  "gc": {
    "num_gc": %d,
    "num_forced_gc": %d,
    "pause_total_ns": %d,
    "pause_ns": %d,
    "gc_cpu_fraction": %f
  },
  "goroutines": {
    "count": %d
  }
}`,
		formatMemStats(m),
		m.NumGC,
		m.NumForcedGC,
		m.PauseTotalNs,
		m.PauseNs[(m.NumGC+gcPauseIndexOffset)%gcPauseHistorySize],
		m.GCCPUFraction,
		runtime.NumGoroutine(),
	); err != nil {
		http.Error(w, "failed to write metrics", http.StatusInternalServerError)
	}
}

func formatMemStats(m *runtime.MemStats) string {
	return fmt.Sprintf(`{
    "alloc_bytes": %d,
    "total_alloc_bytes": %d,
    "sys_bytes": %d,
    "heap_alloc_bytes": %d,
    "heap_sys_bytes": %d,
    "heap_idle_bytes": %d,
    "heap_inuse_bytes": %d,
    "heap_released_bytes": %d,
    "heap_objects": %d,
    "stack_inuse_bytes": %d,
    "stack_sys_bytes": %d,
    "mspan_inuse_bytes": %d,
    "mspan_sys_bytes": %d,
    "mcache_inuse_bytes": %d,
    "mcache_sys_bytes": %d,
    "buck_hash_sys_bytes": %d,
    "gc_sys_bytes": %d,
    "other_sys_bytes": %d,
    "next_gc_bytes": %d
  }`,
		m.Alloc,
		m.TotalAlloc,
		m.Sys,
		m.HeapAlloc,
		m.HeapSys,
		m.HeapIdle,
		m.HeapInuse,
		m.HeapReleased,
		m.HeapObjects,
		m.StackInuse,
		m.StackSys,
		m.MSpanInuse,
		m.MSpanSys,
		m.MCacheInuse,
		m.MCacheSys,
		m.BuckHashSys,
		m.GCSys,
		m.OtherSys,
		m.NextGC,
	)
}

// healthHandler returns basic health check information
func healthHandler(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if _, err := fmt.Fprintf(w, `{
  "status": "ok",
  "timestamp": "%s",
  "goroutines": %d,
  "go_version": "%s",
  "num_cpu": %d
}`,
		time.Now().Format(time.RFC3339),
		runtime.NumGoroutine(),
		runtime.Version(),
		runtime.NumCPU(),
	); err != nil {
		http.Error(w, "failed to write health response", http.StatusInternalServerError)
	}
}
