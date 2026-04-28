package database

import (
	"context"

	"github.com/georgysavva/scany/v2/pgxscan"
)

// Select is a small convenience wrapper around pgxscan.Select that keeps
// the dependency localized in the database package.
//
// Example:
//
//	var rows []MyRow
//	err := database.Select(ctx, pool, &rows, `SELECT ...`, args...)
func Select(ctx context.Context, db pgxscan.Querier, dest interface{}, query string, args ...interface{}) error {
	return pgxscan.Select(ctx, db, dest, query, args...)
}

// Get is a convenience wrapper around pgxscan.Get for querying a single row.
func Get(ctx context.Context, db pgxscan.Querier, dest interface{}, query string, args ...interface{}) error {
	return pgxscan.Get(ctx, db, dest, query, args...)
}
