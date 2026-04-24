package db

import (
	"database/sql"
	"errors"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/jackc/pgx/v5"
)

// ScanItem scans a single row into an Item
func ScanItem(row pgx.Row) (*Item, error) {
	var item Item
	err := row.Scan(
		&item.ID,
		&item.ProjectID,
		&item.Title,
		&item.Description,
		&item.Type,
		&item.Status,
		&item.Priority,
		&item.Metadata,
		&item.SearchVector,
		&item.Embedding,
		&item.CreatedAt,
		&item.UpdatedAt,
		&item.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("item not found")
		}
		return nil, err
	}
	return &item, nil
}

// ScanItems scans multiple rows into Item slices using scany
func ScanItems(rows pgx.Rows) ([]*Item, error) {
	defer rows.Close()
	var items []*Item
	err := pgxscan.ScanAll(&items, rows)
	if err != nil {
		return nil, err
	}
	return items, nil
}

// ScanLink scans a single row into a Link
func ScanLink(row pgx.Row) (*Link, error) {
	var link Link
	err := row.Scan(
		&link.ID,
		&link.SourceID,
		&link.TargetID,
		&link.Type,
		&link.Metadata,
		&link.CreatedAt,
		&link.UpdatedAt,
		&link.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("link not found")
		}
		return nil, err
	}
	return &link, nil
}

// ScanLinks scans multiple rows into Link slices using scany
func ScanLinks(rows pgx.Rows) ([]*Link, error) {
	defer rows.Close()
	var links []*Link
	err := pgxscan.ScanAll(&links, rows)
	if err != nil {
		return nil, err
	}
	return links, nil
}

// ScanProject scans a single row into a Project
func ScanProject(row pgx.Row) (*Project, error) {
	var project Project
	err := row.Scan(
		&project.ID,
		&project.Name,
		&project.Description,
		&project.Metadata,
		&project.CreatedAt,
		&project.UpdatedAt,
		&project.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("project not found")
		}
		return nil, err
	}
	return &project, nil
}

// ScanProjects scans multiple rows into Project slices using scany
func ScanProjects(rows pgx.Rows) ([]*Project, error) {
	defer rows.Close()
	var projects []*Project
	err := pgxscan.ScanAll(&projects, rows)
	if err != nil {
		return nil, err
	}
	return projects, nil
}

// ScanAgent scans a single row into an Agent
func ScanAgent(row pgx.Row) (*Agent, error) {
	var agent Agent
	err := row.Scan(
		&agent.ID,
		&agent.ProjectID,
		&agent.Name,
		&agent.Status,
		&agent.Metadata,
		&agent.LastActivityAt,
		&agent.CreatedAt,
		&agent.UpdatedAt,
		&agent.DeletedAt,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("agent not found")
		}
		return nil, err
	}
	return &agent, nil
}

// ScanAgents scans multiple rows into Agent slices using scany
func ScanAgents(rows pgx.Rows) ([]*Agent, error) {
	defer rows.Close()
	var agents []*Agent
	err := pgxscan.ScanAll(&agents, rows)
	if err != nil {
		return nil, err
	}
	return agents, nil
}

// ScanDescendants scans the recursive descendant query results
func ScanDescendants(rows pgx.Rows) ([]*GetDescendantsRow, error) {
	defer rows.Close()
	var results []*GetDescendantsRow
	err := pgxscan.ScanAll(&results, rows)
	if err != nil {
		return nil, err
	}
	return results, nil
}

// ScanAncestors scans the recursive ancestor query results
func ScanAncestors(rows pgx.Rows) ([]*GetAncestorsRow, error) {
	defer rows.Close()
	var results []*GetAncestorsRow
	err := pgxscan.ScanAll(&results, rows)
	if err != nil {
		return nil, err
	}
	return results, nil
}
