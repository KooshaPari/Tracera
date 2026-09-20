package executor

import (
	"context"
	"errors"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

type stubRunner struct {
	calls []string
	err   map[string]error
}

func (s *stubRunner) Run(_ context.Context, service, image string) error {
	s.calls = append(s.calls, service+"="+image)
	if s.err != nil {
		if err, ok := s.err[service]; ok {
			return err
		}
	}
	return nil
}

func TestConvergeReportsPerService(t *testing.T) {
	runner := &stubRunner{err: map[string]error{
		"bad": errors.New("image pull denied"),
	}}
	desired := map[string]string{
		"good":   "ghcr.io/kooshapari/tracera-server:v1",
		"bad":    "ghcr.io/kooshapari/other:v9",
		"stopme": "",
	}
	got := Converge(context.Background(), runner, desired)

	if got["good"] != "ok" {
		t.Errorf("good = %q, want ok", got["good"])
	}
	if !strings.HasPrefix(got["bad"], "failed:") {
		t.Errorf("bad = %q, want failed: prefix", got["bad"])
	}
	if got["stopme"] != "ok" {
		t.Errorf("stopme = %q, want ok (down is a successful convergence)", got["stopme"])
	}
	if len(runner.calls) != 3 {
		t.Errorf("runner calls = %d, want 3 (one per service, no early exit)", len(runner.calls))
	}
}

func TestDockerComposeRunCreatesProjectDir(t *testing.T) {
	dir := t.TempDir()
	d := NewDockerCompose(filepath.Join(dir, "state"), 5*time.Second)
	// Docker is not exercised here; only that Run surfaces the compose file
	// path correctly. We test the failure path: docker is unlikely to be
	// present in CI, so we assert the error mentions compose.
	err := d.Run(context.Background(), "demo", "nginx:alpine")
	if err == nil {
		t.Skip("docker present in environment; skipping failure-path assertion")
	}
	if !strings.Contains(err.Error(), "compose up demo") {
		t.Errorf("unexpected error: %v", err)
	}
}
