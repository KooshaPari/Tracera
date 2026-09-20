package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"os/user"
	"runtime"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/kooshapari/tracera-sidecar/internal/config"
	"github.com/kooshapari/tracera-sidecar/internal/executor"
	"github.com/kooshapari/tracera-sidecar/internal/nodeapi"
)

func main() {
	ctx := config.InitializeContext()
	if !ctx.Enabled {
		slog.Info("tracera-sidecar disabled", "env", "TRACERA_SIDE_CAR_ENABLED", "value", "false")
		return
	}

	// The control-plane mode requires three env vars. Without them the
	// sidecar falls back to legacy heartbeat-only behavior so the existing
	// contract is preserved.
	if ctx.ControlPlaneBase == "" || ctx.NodeID == "" || ctx.EnrollToken == "" {
		slog.Warn("control-plane env incomplete; falling back to heartbeat-only",
			"control_plane", ctx.ControlPlaneBase != "",
			"node_id", ctx.NodeID != "",
			"enroll_token", ctx.EnrollToken != "")
		runHeartbeatOnly(ctx)
		return
	}

	if err := runNodeAgent(ctx); err != nil {
		slog.Error("node agent exited with error", "err", err)
		os.Exit(1)
	}
}

func runHeartbeatOnly(ctx config.Config) {
	slog.Info("starting tracera-sidecar (heartbeat)", "version", config.Version, "api_base", ctx.APIBase)
	var ticks atomic.Int64
	ticker := time.NewTicker(ctx.PollInterval)
	defer ticker.Stop()
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	for {
		select {
		case <-ticker.C:
			slog.Info("sidecar heartbeat", "tick", ticks.Add(1), "api_base", ctx.APIBase)
		case <-sig:
			slog.Info("stopping tracera-sidecar")
			return
		}
	}
}

func runNodeAgent(cfg config.Config) error {
	slog.Info("starting tracera-sidecar (node agent)",
		"version", config.Version,
		"control_plane", cfg.ControlPlaneBase,
		"node_id", cfg.NodeID,
		"state_dir", cfg.StateDir,
		"poll", cfg.PollInterval)

	client := nodeapi.NewClient(cfg.ControlPlaneBase, cfg.EnrollToken, 30*time.Second)

	// Caps are basic facts about this box so the control plane can make
	// placement decisions later. Keep them cheap and honest.
	caps := map[string]string{
		"os":   runtime.GOOS,
		"arch": runtime.GOARCH,
	}
	if u, err := user.Current(); err == nil {
		caps["user"] = u.Username
	}
	if h, err := os.Hostname(); err == nil {
		caps["hostname"] = h
	}

	// Enroll on startup. A rejected enroll is fatal: the node should not
	// run services the control plane has not acknowledged.
	bg := context.Background()
	enrollResp, err := client.Enroll(bg, nodeapi.EnrollRequest{
		NodeID:     cfg.NodeID,
		Caps:       caps,
		SidecarVer: config.Version,
	})
	if err != nil {
		return err
	}
	slog.Info("enrolled", "generation", enrollResp.Generation)

	executorRunner := executor.NewDockerCompose(cfg.StateDir, cfg.ConvergeTimeout)

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)

	var lastGeneration = -1
	ticker := time.NewTicker(cfg.PollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			loopCtx, cancel := context.WithTimeout(bg, cfg.PollInterval*3)
			desired, err := client.FetchDesired(loopCtx, cfg.NodeID)
			if err != nil {
				slog.Warn("fetch desired failed", "err", err)
				cancel()
				continue
			}
			if desired.Generation != lastGeneration {
				slog.Info("converging to new desired state",
					"generation", desired.Generation, "services", len(desired.Services))
				results := executor.Converge(loopCtx, executorRunner, desired.Services)
				err = client.Report(loopCtx, nodeapi.Status{
					NodeID:     cfg.NodeID,
					Generation: desired.Generation,
					Services:   map[string]string(results),
					UpdatedAt:  time.Now().UTC(),
				})
				if err != nil {
					slog.Warn("report failed", "err", err)
				} else {
					for svc, res := range results {
						slog.Info("service", "name", svc, "result", res)
					}
				}
				lastGeneration = desired.Generation
			}
			cancel()
		case <-sig:
			slog.Info("stopping tracera-sidecar")
			return nil
		}
	}
}
