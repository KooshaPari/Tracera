// Package main sets up local tracertm infrastructure.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/jackc/pgx/v5"
	"github.com/joho/godotenv"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"

	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/env"
)

func main() {
	var (
		envFile = flag.String("env", ".env", "Path to .env file")
		verify  = flag.Bool("verify", false, "Only verify configuration")
		help    = flag.Bool("help", false, "Show help")
	)
	flag.Parse()

	if *help {
		printHelp()
		os.Exit(0)
	}

	fmt.Println()
	fmt.Println("╔════════════════════════════════════════════════════════════════╗")
	fmt.Println("║         TraceRTM - Automated Database Setup                   ║")
	fmt.Println("╚════════════════════════════════════════════════════════════════╝")

	// Load .env file
	if err := godotenv.Load(*envFile); err != nil {
		log.Printf("⚠️  Could not load %s: %v", *envFile, err)
	}

	// Create environment manager
	envMgr := env.New()
	envMgr.Load()

	// Load configuration
	cfg, err := config.LoadWithEnvManager()
	if err != nil {
		log.Fatalf("❌ Failed to load configuration: %v", err)
	}

	if *verify {
		verifyConfiguration(cfg, envMgr)
		os.Exit(0)
	}

	// Print configuration summary
	printConfigurationSummary(cfg)

	// Setup PostgreSQL
	if err := setupPostgreSQL(cfg); err != nil {
		log.Printf("❌ PostgreSQL setup failed: %v", err)
		os.Exit(1)
	}

	// Setup Neo4j
	if err := setupNeo4j(cfg); err != nil {
		log.Printf("❌ Neo4j setup failed: %v", err)
		os.Exit(1)
	}

	fmt.Println()
	fmt.Println("╔════════════════════════════════════════════════════════════════╗")
	fmt.Println("║              ✅ Database Setup Complete!                      ║")
	fmt.Println("╚════════════════════════════════════════════════════════════════╝")

	fmt.Println("Next steps:")
	fmt.Println("  1. Build: docker build -t tracertm-backend:latest .")
	fmt.Println("  2. Test:  docker-compose -f docker-compose.prod.yml up -d")
	fmt.Println("  3. Check: curl http://localhost:8080/health")
}

func setupPostgreSQL(cfg *config.Config) error {
	fmt.Println("📝 Setting up PostgreSQL (Supabase)...")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	dbURL := cfg.DatabaseURL
	if dbURL == "" {
		return errors.New("DATABASE_URL not set")
	}

	ctx := context.Background()
	conn, err := pgx.Connect(ctx, dbURL)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer func() {
		if err := conn.Close(ctx); err != nil {
			log.Printf("error closing connection: %v", err)
		}
	}()

	// Create extensions
	extensions := []string{"uuid-ossp", "pg_trgm", "vector"}
	for _, ext := range extensions {
		sql := fmt.Sprintf(`CREATE EXTENSION IF NOT EXISTS "%s";`, ext)
		if _, err := conn.Exec(ctx, sql); err != nil {
			fmt.Printf("  ⚠️  Extension %s: %v\n", ext, err)
		} else {
			fmt.Printf("  ✅ Extension %s created\n", ext)
		}
	}

	// Apply migrations
	schemaSQL, err := os.ReadFile("schema.sql")
	if err != nil {
		return fmt.Errorf("failed to read schema.sql: %w", err)
	}

	if _, err := conn.Exec(ctx, string(schemaSQL)); err != nil {
		return fmt.Errorf("failed to apply schema: %w", err)
	}
	fmt.Println("  ✅ Migrations applied")

	// Verify tables
	var count int
	const tableCountQuery = `SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';`
	err = conn.QueryRow(ctx, tableCountQuery).Scan(&count)
	if err == nil {
		fmt.Printf("  ✅ Tables created: %d\n", count)
	}

	fmt.Println()
	return nil
}

func setupNeo4j(cfg *config.Config) error {
	fmt.Println("📝 Setting up Neo4j (Aura)...")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	uri, username, password := cfg.Neo4jURI, cfg.Neo4jUser, cfg.Neo4jPassword

	if uri == "" || username == "" || password == "" {
		return errors.New("Neo4j credentials not set")
	}

	// Use Neo4j driver with context
	ctx := context.Background()
	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(username, password, ""))
	if err != nil {
		return fmt.Errorf("failed to create driver: %w", err)
	}
	defer func() {
		if err := driver.Close(ctx); err != nil {
			log.Printf("error closing driver: %v", err)
		}
	}()

	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer func() {
		if err := session.Close(ctx); err != nil {
			log.Printf("error closing session: %v", err)
		}
	}()

	if err := createNeo4jConstraints(ctx, session); err != nil {
		return err
	}
	if err := createNeo4jIndexes(ctx, session); err != nil {
		return err
	}

	fmt.Println()
	return nil
}

func createNeo4jConstraints(ctx context.Context, session neo4j.SessionWithContext) error {
	constraints := []string{
		"CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.item_id IS UNIQUE;",
		"CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.project_id IS UNIQUE;",
		"CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;",
	}
	for _, constraint := range constraints {
		if _, err := session.Run(ctx, constraint, nil); err != nil {
			fmt.Printf("  ⚠️  Constraint: %v\n", err)
		} else {
			fmt.Println("  ✅ Constraint created")
		}
	}
	return nil
}

func createNeo4jIndexes(ctx context.Context, session neo4j.SessionWithContext) error {
	indexes := []string{
		"CREATE INDEX project_id_idx IF NOT EXISTS FOR (n) ON (n.project_id);",
		"CREATE INDEX type_idx IF NOT EXISTS FOR (n) ON (n.type);",
		"CREATE INDEX name_idx IF NOT EXISTS FOR (n) ON (n.name);",
	}
	for _, index := range indexes {
		if _, err := session.Run(ctx, index, nil); err != nil {
			fmt.Printf("  ⚠️  Index: %v\n", err)
		} else {
			fmt.Println("  ✅ Index created")
		}
	}
	return nil
}

func verifyConfiguration(cfg *config.Config, _ *env.Manager) {
	fmt.Println()
	fmt.Println("🔍 Verifying Configuration...")
	fmt.Println()

	checks := buildConfigChecks(cfg)
	passed, failed := runConfigChecks(checks)

	fmt.Printf("\n📊 Results: %d passed, %d failed\n", passed, failed)

	if failed > 0 {
		os.Exit(1)
	}
}

type configCheck struct {
	name  string
	check func() error
}

func buildConfigChecks(cfg *config.Config) []configCheck {
	return []configCheck{
		{
			name: "Database URL",
			check: func() error {
				if cfg.DatabaseURL == "" {
					return errors.New("DATABASE_URL not set")
				}
				return nil
			},
		},
		{
			name: "Redis URL",
			check: func() error {
				if cfg.RedisURL == "" && cfg.UpstashRedisRestURL == "" {
					return errors.New("REDIS_URL or UPSTASH_REDIS_REST_URL must be set")
				}
				return nil
			},
		},
		{
			name: "NATS URL",
			check: func() error {
				if cfg.NATSUrl == "" {
					return errors.New("NATS_URL not set")
				}
				return nil
			},
		},
		{
			name: "Neo4j URI",
			check: func() error {
				if cfg.Neo4jURI == "" {
					return errors.New("NEO4J_URI not set")
				}
				return nil
			},
		},
	}
}

func runConfigChecks(checks []configCheck) (int, int) {
	passed := 0
	failed := 0
	for _, check := range checks {
		if err := check.check(); err != nil {
			fmt.Printf("❌ %s: %v\n", check.name, err)
			failed++
			continue
		}
		fmt.Printf("✅ %s\n", check.name)
		passed++
	}
	return passed, failed
}

func printConfigurationSummary(cfg *config.Config) {
	fmt.Println()
	fmt.Println("📋 Configuration Summary:")
	fmt.Printf("  Environment:     %s\n", cfg.Env)
	fmt.Printf("  Port:            %s\n", cfg.Port)
	fmt.Printf("  Database:        %s\n", maskSensitive(cfg.DatabaseURL))
	fmt.Printf("  Redis:           %s\n", maskSensitive(cfg.RedisURL))
	fmt.Printf("  NATS:            %s\n", cfg.NATSUrl)
	fmt.Printf("  Neo4j:           %s\n", cfg.Neo4jURI)
	fmt.Println()
}

func maskSensitive(value string) string {
	const (
		maskThreshold    = 20
		maskPrefixLength = 10
		maskSuffixLength = 10
	)

	if len(value) > maskThreshold {
		return value[:maskPrefixLength] + "..." + value[len(value)-maskSuffixLength:]
	}
	return value
}

func printHelp() {
	fmt.Print(`
TraceRTM Environment Setup

Usage:
  setup [flags]

Flags:
  -env string
    	Path to .env file (default ".env")
  -verify
    	Only verify configuration without setting up
  -help
    	Show this help message

Examples:
  # Setup with default .env
  setup

  # Setup with custom .env file
  setup -env .env.production

  # Verify configuration
  setup -verify

	  # Verify with custom .env file
	  setup -env .env.staging -verify
	`)
}
