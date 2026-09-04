// Command tracera is a minimal stdlib-only CLI for the Tracera REST API.
//
// Usage:
//
//	tracera serve [--addr :8080]          # start a thin local proxy on the Tracera API
//	tracera ingest <source> [--file FILE] # POST to /ingest/{github|jira|agileplus}
//	tracera query <kind> [--q Q] [--top N]# POST to /api/v1/{infer|suggest|classify|search}
//	tracera graph <op> [--id ID] [--depth N] [--direction fwd|rev|both]
//	tracera node <id>                    # GET /api/v1/items/{id}
//
// Environment:
//
//	TRACERA_BASE_URL  Base URL (default http://127.0.0.1:8080)
//	TRACERA_TOKEN     Optional bearer token
//	TRACERA_TIMEOUT   HTTP timeout (Go duration, default 30s)
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"
)

// -----------------------------------------------------------------------------
// Shared client
// -----------------------------------------------------------------------------

// client is a tiny wrapper over net/http that handles auth, base URL,
// timeout, and JSON encoding. It is intentionally stdlib-only.
type client struct {
	baseURL string
	token   string
	http    *http.Client
}

// newClient builds a client from environment variables.
func newClient() *client {
	base := envOr("TRACERA_BASE_URL", "http://127.0.0.1:8080")
	base = strings.TrimRight(base, "/")

	timeout := 30 * time.Second
	if raw := os.Getenv("TRACERA_TIMEOUT"); raw != "" {
		if d, err := time.ParseDuration(raw); err == nil && d > 0 {
			timeout = d
		}
	}

	return &client{
		baseURL: base,
		token:   os.Getenv("TRACERA_TOKEN"),
		http:    &http.Client{Timeout: timeout},
	}
}

// do performs an HTTP request and returns the response body. Errors are wrapped
// with status code information so callers can present useful diagnostics.
func (c *client) do(ctx context.Context, method, path string, body any, out any) error {
	var rdr io.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("marshal request: %w", err)
		}
		rdr = bytes.NewReader(buf)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, rdr)
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	req.Header.Set("Accept", "application/json")
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return fmt.Errorf("request %s %s: %w", method, path, err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		return &apiError{Status: resp.StatusCode, Body: strings.TrimSpace(string(respBody))}
	}

	if out != nil && len(respBody) > 0 {
		if err := json.Unmarshal(respBody, out); err != nil {
			return fmt.Errorf("decode response: %w", err)
		}
	}
	return nil
}

// apiError surfaces non-2xx responses with their status code and body.
type apiError struct {
	Status int
	Body   string
}

func (e *apiError) Error() string {
	if e.Body == "" {
		return fmt.Sprintf("HTTP %d", e.Status)
	}
	return fmt.Sprintf("HTTP %d: %s", e.Status, e.Body)
}

// envOr returns the env var or a fallback.
func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// writeJSON pretty-prints v (or raw bytes if already JSON). Falls back to %v.
func writeJSON(v any) error {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(v); err != nil {
		// Fall back to raw output
		if b, ok := v.([]byte); ok {
			_, err := os.Stdout.Write(b)
			return err
		}
		fmt.Fprintln(os.Stdout, v)
	}
	return nil
}

// -----------------------------------------------------------------------------
// Subcommand: serve
// -----------------------------------------------------------------------------
//
// `tracera serve` runs a small reverse-proxy in front of the upstream Tracera
// REST API. It is intended for local development and for environments that
// benefit from a single auth-injecting entry point. The proxy does not buffer
// responses — it streams them as they come back.

func cmdServe(args []string) error {
	fs := flag.NewFlagSet("serve", flag.ExitOnError)
	addr := fs.String("addr", envOr("TRACERA_PROXY_ADDR", "127.0.0.1:7790"), "listen address")
	upstream := fs.String("upstream", envOr("TRACERA_BASE_URL", "http://127.0.0.1:8080"), "upstream base URL")
	if err := fs.Parse(args); err != nil {
		return err
	}

	c := newClient()
	up := strings.TrimRight(*upstream, "/")

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 60*time.Second)
		defer cancel()

		var body io.Reader
		if r.Body != nil {
			body = r.Body
		}
		req, err := http.NewRequestWithContext(ctx, r.Method, up+r.URL.RequestURI(), body)
		if err != nil {
			http.Error(w, "build request: "+err.Error(), http.StatusInternalServerError)
			return
		}
		for k, vs := range r.Header {
			for _, v := range vs {
				req.Header.Add(k, v)
			}
		}
		if c.token != "" {
			req.Header.Set("Authorization", "Bearer "+c.token)
		}

		resp, err := c.http.Do(req)
		if err != nil {
			http.Error(w, "upstream: "+err.Error(), http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()
		for k, vs := range resp.Header {
			for _, v := range vs {
				w.Header().Add(k, v)
			}
		}
		w.WriteHeader(resp.StatusCode)
		_, _ = io.Copy(w, resp.Body)
	})

	srv := &http.Server{
		Addr:              *addr,
		Handler:           mux,
		ReadHeaderTimeout: 10 * time.Second,
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	errCh := make(chan error, 1)
	go func() { errCh <- srv.ListenAndServe() }()

	fmt.Fprintf(os.Stderr, "tracera serve: listening on %s -> %s\n", *addr, up)

	select {
	case <-ctx.Done():
		fmt.Fprintln(os.Stderr, "tracera serve: shutting down")
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		return srv.Shutdown(shutdownCtx)
	case err := <-errCh:
		if errors.Is(err, http.ErrServerClosed) {
			return nil
		}
		return err
	}
}

// -----------------------------------------------------------------------------
// Subcommand: ingest
// -----------------------------------------------------------------------------
//
// `tracera ingest github|jira|agileplus [--file FILE]` POSTs a JSON payload to
// the corresponding /ingest/<source> endpoint. If --file is omitted, stdin is
// read in full and used as the body.

func cmdIngest(args []string) error {
	fs := flag.NewFlagSet("ingest", flag.ExitOnError)
	file := fs.String("file", "", "path to JSON payload (default: stdin)")
	if err := fs.Parse(args); err != nil {
		return err
	}
	rest := fs.Args()
	if len(rest) < 1 {
		return errors.New("usage: tracera ingest <github|jira|agileplus> [--file FILE]")
	}
	source := rest[0]
	switch source {
	case "github", "jira", "agileplus":
	default:
		return fmt.Errorf("unknown ingest source %q (want github|jira|agileplus)", source)
	}

	payload, err := readPayload(*file)
	if err != nil {
		return err
	}

	var out json.RawMessage
	if err := newClient().do(context.Background(), http.MethodPost, "/ingest/"+source, json.RawMessage(payload), &out); err != nil {
		return err
	}
	return writeJSON(out)
}

// readPayload reads the JSON payload from path or stdin.
func readPayload(path string) ([]byte, error) {
	if path == "" || path == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(path)
}

// -----------------------------------------------------------------------------
// Subcommand: query
// -----------------------------------------------------------------------------
//
// `tracera query <infer|suggest|classify|search|confidence> [--q Q] [--top N]`
// POSTs to /api/v1/<kind>.

func cmdQuery(args []string) error {
	fs := flag.NewFlagSet("query", flag.ExitOnError)
	q := fs.String("q", "", "query string")
	top := fs.Int("top", 10, "max results to return")
	if err := fs.Parse(args); err != nil {
		return err
	}
	rest := fs.Args()
	if len(rest) < 1 {
		return errors.New("usage: tracera query <infer|suggest|classify|search|confidence> [--q Q] [--top N]")
	}
	kind := rest[0]
	switch kind {
	case "infer", "suggest", "classify", "search", "confidence":
	default:
		return fmt.Errorf("unknown query kind %q", kind)
	}

	body := map[string]any{"query": *q, "top_k": *top}
	var out json.RawMessage
	if err := newClient().do(context.Background(), http.MethodPost, "/api/v1/"+kind, body, &out); err != nil {
		return err
	}
	return writeJSON(out)
}

// -----------------------------------------------------------------------------
// Subcommand: graph
// -----------------------------------------------------------------------------
//
// `tracera graph <op> [--id ID] [--depth N] [--direction fwd|rev|both]`
//
//	op is one of: ancestors, descendants, impact, dependencies, traverse, full, cycles, orphans, path.

func cmdGraph(args []string) error {
	fs := flag.NewFlagSet("graph", flag.ExitOnError)
	id := fs.String("id", "", "node id")
	depth := fs.Int("depth", 3, "traversal depth")
	direction := fs.String("direction", "both", "traversal direction: fwd|rev|both")
	if err := fs.Parse(args); err != nil {
		return err
	}
	rest := fs.Args()
	if len(rest) < 1 {
		return errors.New("usage: tracera graph <op> [--id ID] [--depth N] [--direction fwd|rev|both]")
	}
	op := rest[0]

	var path string
	var body map[string]any

	switch op {
	case "ancestors", "descendants", "impact", "dependencies", "traverse":
		if *id == "" {
			return fmt.Errorf("--id is required for graph %s", op)
		}
		path = "/api/v1/graph/" + op + "/" + *id
		body = map[string]any{"depth": *depth, "direction": *direction}

	case "full":
		path = "/api/v1/graph/full"
		body = map[string]any{"max_depth": *depth}

	case "cycles", "orphans":
		path = "/api/v1/graph/" + op
		body = map[string]any{}

	case "path":
		if *id == "" {
			return errors.New("--id is required for graph path (use target/source as id1,id2)")
		}
		ids := strings.SplitN(*id, ",", 2)
		if len(ids) != 2 {
			return errors.New("graph path --id expects 'SOURCE,TARGET'")
		}
		path = "/api/v1/graph/path"
		body = map[string]any{"source": ids[0], "target": ids[1], "max_depth": *depth}

	default:
		return fmt.Errorf("unknown graph op %q", op)
	}

	var out json.RawMessage
	if err := newClient().do(context.Background(), http.MethodPost, path, body, &out); err != nil {
		return err
	}
	return writeJSON(out)
}

// -----------------------------------------------------------------------------
// Subcommand: node
// -----------------------------------------------------------------------------
//
// `tracera node <id>` GETs /api/v1/items/{id} and prints it.

func cmdNode(args []string) error {
	fs := flag.NewFlagSet("node", flag.ExitOnError)
	if err := fs.Parse(args); err != nil {
		return err
	}
	rest := fs.Args()
	if len(rest) < 1 {
		return errors.New("usage: tracera node <id>")
	}
	id := rest[0]
	if _, err := strconv.Atoi(id); err != nil {
		// allow non-numeric IDs by URL-escaping via the path builder.
		// net/http will not escape for us so we trust the caller for non-numeric IDs.
	}

	var out json.RawMessage
	if err := newClient().do(context.Background(), http.MethodGet, "/api/v1/items/"+id, nil, &out); err != nil {
		return err
	}
	return writeJSON(out)
}

// -----------------------------------------------------------------------------
// Entry point
// -----------------------------------------------------------------------------

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	cmd, args := os.Args[1], os.Args[2:]
	var err error
	switch cmd {
	case "serve":
		err = cmdServe(args)
	case "ingest":
		err = cmdIngest(args)
	case "query":
		err = cmdQuery(args)
	case "graph":
		err = cmdGraph(args)
	case "node":
		err = cmdNode(args)
	case "-h", "--help", "help":
		usage()
		return
	default:
		fmt.Fprintf(os.Stderr, "unknown command %q\n\n", cmd)
		usage()
		os.Exit(2)
	}

	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func usage() {
	fmt.Fprintf(os.Stderr, `tracera — minimal CLI for the Tracera REST API (stdlib only)

Usage:
  tracera <command> [flags]

Commands:
  serve      Run a thin local reverse-proxy in front of the Tracera API
  ingest     POST to /ingest/{github|jira|agileplus}
  query      POST to /api/v1/{infer|suggest|classify|search|confidence}
  graph      POST to /api/v1/graph/* (ancestors, descendants, impact, ...)
  node       GET /api/v1/items/{id}

Environment:
  TRACERA_BASE_URL  Base URL (default http://127.0.0.1:8080)
  TRACERA_TOKEN     Optional bearer token
  TRACERA_TIMEOUT   HTTP timeout (default 30s)
  TRACERA_PROXY_ADDR Listen address when running 'serve' (default 127.0.0.1:7790)

Run 'tracera <command> -h' for command-specific help.
`)
}