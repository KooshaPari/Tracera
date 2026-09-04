module github.com/kooshapari/tracera/go-cli

go 1.22

// tracera-go-cli is a stdlib-only minimal CLI that calls the Tracera REST API.
// Subcommands: serve, ingest, query, graph, node.
//
// Install (after release):
//
//	go install github.com/kooshapari/tracera/go-cli/cmd/tracera@latest
//
// Or build from source:
//
//	cd crates/tracera-go-cli && go build -o bin/tracera .
//
// Configuration is via environment variables (no flag/config file is required):
//
//	TRACERA_BASE_URL  Base URL of the Tracera REST API. Default http://127.0.0.1:8080
//	TRACERA_TOKEN     Optional bearer token. Sent as `Authorization: Bearer <token>`.
//	TRACERA_TIMEOUT   HTTP client timeout (Go duration, e.g. 30s). Default 30s.