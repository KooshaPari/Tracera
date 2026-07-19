package main

import (
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/kooshapari/tracera-sidecar/internal/config"
)

func main() {
	ctx := config.InitializeContext()
	if !ctx.Enabled {
		slog.Info("tracera-sidecar disabled", "env", "TRACERA_SIDE_CAR_ENABLED", "value", "false")
		return
	}

	slog.Info("starting tracera-sidecar", "version", config.Version)
	slog.Info("sidecar configuration", "api_base", ctx.APIBase, "poll_interval_seconds", int(ctx.PollInterval.Seconds()))

	// Lightweight readiness marker for future orchestration path wiring.
	var ticks atomic.Int64
	ticker := time.NewTicker(ctx.PollInterval)
	defer ticker.Stop()

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)

	for {
		select {
		case <-ticker.C:
			ticks.Add(1)
			fmt.Printf("sidecar_tick=%d api_base=%s\n", ticks.Load(), ctx.APIBase)
		case <-sig:
			slog.Info("stopping tracera-sidecar")
			return
		}
	}
}
