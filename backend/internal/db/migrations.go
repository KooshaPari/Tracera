package db

import (
	"context"
	"database/sql"
	"embed"
	"fmt"
	"log/slog"
	"sort"
	"strings"
)

const migrationNamePartsMin = 2

//go:embed migrations/*.sql
var migrations embed.FS

// MigrationRecord represents a migration that has been applied
type MigrationRecord struct {
	Version string
	Name    string
}

// RunMigrations applies all pending migrations to the database
func RunMigrations(ctx context.Context, db *sql.DB) error {
	// Create migrations table if it doesn't exist
	if err := createMigrationsTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create migrations table: %w", err)
	}

	// Get list of applied migrations
	applied, err := getAppliedMigrations(ctx, db)
	if err != nil {
		return fmt.Errorf("failed to get applied migrations: %w", err)
	}

	// Get list of available migrations
	available, err := getAvailableMigrations()
	if err != nil {
		return fmt.Errorf("failed to get available migrations: %w", err)
	}

	// Apply pending migrations
	for _, migration := range available {
		if _, exists := applied[migration.Version]; exists {
			continue
		}

		slog.Info("Applying migration", "detail", migration.Version, "name", migration.Name)
		if err := applyMigration(ctx, db, migration); err != nil {
			return fmt.Errorf("failed to apply migration %s: %w", migration.Version, err)
		}

		// Record migration as applied
		if err := recordMigration(ctx, db, migration); err != nil {
			return fmt.Errorf("failed to record migration %s: %w", migration.Version, err)
		}
	}

	return nil
}

// createMigrationsTable creates the schema_migrations table if it doesn't exist
func createMigrationsTable(ctx context.Context, db *sql.DB) error {
	query := `
		CREATE TABLE IF NOT EXISTS schema_migrations (
			version varchar(255) PRIMARY KEY,
			name varchar(255) NOT NULL,
			applied_at timestamp NOT NULL DEFAULT now()
		)
	`
	_, err := db.ExecContext(ctx, query)
	return err
}

// getAppliedMigrations returns a map of applied migration versions
func getAppliedMigrations(ctx context.Context, db *sql.DB) (applied map[string]bool, err error) {
	rows, err := db.QueryContext(ctx, "SELECT version FROM schema_migrations")
	if err != nil {
		return nil, err
	}
	defer func() {
		if closeErr := rows.Close(); closeErr != nil && err == nil {
			err = closeErr
		}
	}()

	applied = make(map[string]bool)
	for rows.Next() {
		var version string
		if scanErr := rows.Scan(&version); scanErr != nil {
			return nil, scanErr
		}
		applied[version] = true
	}

	if rowsErr := rows.Err(); rowsErr != nil {
		return nil, rowsErr
	}

	return applied, nil
}

// getAvailableMigrations returns a sorted list of available migrations
func getAvailableMigrations() ([]MigrationRecord, error) {
	entries, err := migrations.ReadDir("migrations")
	if err != nil {
		return nil, err
	}

	var records []MigrationRecord
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".sql") {
			continue
		}

		// Parse filename: YYYYMMDDHHMMSS_name.sql
		parts := strings.Split(entry.Name(), "_")
		if len(parts) < migrationNamePartsMin {
			continue
		}

		version := parts[0]
		name := strings.TrimSuffix(strings.Join(parts[1:], "_"), ".sql")

		records = append(records, MigrationRecord{
			Version: version,
			Name:    name,
		})
	}

	// Sort by version
	sort.Slice(records, func(i, j int) bool {
		return records[i].Version < records[j].Version
	})

	return records, nil
}

// applyMigration executes a migration file
func applyMigration(ctx context.Context, db *sql.DB, migration MigrationRecord) error {
	filename := fmt.Sprintf("migrations/%s_%s.sql", migration.Version, migration.Name)
	content, err := migrations.ReadFile(filename)
	if err != nil {
		return err
	}

	// Execute migration
	_, err = db.ExecContext(ctx, string(content))
	return err
}

// recordMigration records a migration as applied
func recordMigration(ctx context.Context, db *sql.DB, migration MigrationRecord) error {
	query := `
		INSERT INTO schema_migrations (version, name)
		VALUES ($1, $2)
	`
	_, err := db.ExecContext(ctx, query, migration.Version, migration.Name)
	return err
}
