package search

import (
	"fmt"
	"strings"
)

// QueryBuilder dynamically constructs SQL queries
type QueryBuilder struct {
	selectCols  []string
	fromTable   string
	whereClause []string
	orderBy     []string
	limitVal    int
	offsetVal   int
	args        []interface{}
	argIndex    int
}

// NewQueryBuilder creates a new query builder
func NewQueryBuilder() *QueryBuilder {
	return &QueryBuilder{
		selectCols:  []string{},
		whereClause: []string{},
		orderBy:     []string{},
		args:        []interface{}{},
		argIndex:    1,
	}
}

// Select adds columns to SELECT clause
func (qb *QueryBuilder) Select(cols ...string) *QueryBuilder {
	qb.selectCols = append(qb.selectCols, cols...)
	return qb
}

// From sets the FROM table
func (qb *QueryBuilder) From(table string) *QueryBuilder {
	qb.fromTable = table
	return qb
}

// Where adds a WHERE condition
func (qb *QueryBuilder) Where(condition string, args ...interface{}) *QueryBuilder {
	// Replace ? placeholders with $1, $2, etc.
	for range args {
		condition = strings.Replace(condition, "?", fmt.Sprintf("$%d", qb.argIndex), 1)
		qb.argIndex++
	}
	qb.whereClause = append(qb.whereClause, condition)
	qb.args = append(qb.args, args...)
	return qb
}

// OrderBy adds ORDER BY clause
func (qb *QueryBuilder) OrderBy(field, direction string) *QueryBuilder {
	direction = strings.ToUpper(direction)
	if direction != "ASC" && direction != "DESC" {
		direction = "ASC"
	}
	qb.orderBy = append(qb.orderBy, fmt.Sprintf("%s %s", field, direction))
	return qb
}

// Limit sets LIMIT
func (qb *QueryBuilder) Limit(limit int) *QueryBuilder {
	qb.limitVal = limit
	return qb
}

// Offset sets OFFSET
func (qb *QueryBuilder) Offset(offset int) *QueryBuilder {
	qb.offsetVal = offset
	return qb
}

// Build constructs the final SQL query and returns query string and args
func (qb *QueryBuilder) Build() (string, []interface{}) {
	var query strings.Builder

	// SELECT
	query.WriteString("SELECT ")
	if len(qb.selectCols) > 0 {
		query.WriteString(strings.Join(qb.selectCols, ", "))
	} else {
		query.WriteString("*")
	}

	// FROM
	if qb.fromTable != "" {
		query.WriteString(" FROM ")
		query.WriteString(qb.fromTable)
	}

	// WHERE
	if len(qb.whereClause) > 0 {
		query.WriteString(" WHERE ")
		query.WriteString(strings.Join(qb.whereClause, " AND "))
	}

	// ORDER BY
	if len(qb.orderBy) > 0 {
		query.WriteString(" ORDER BY ")
		query.WriteString(strings.Join(qb.orderBy, ", "))
	}

	// LIMIT
	if qb.limitVal > 0 {
		query.WriteString(fmt.Sprintf(" LIMIT $%d", qb.argIndex))
		qb.args = append(qb.args, qb.limitVal)
		qb.argIndex++

		// If LIMIT is set, always include OFFSET (default to 0 if not set)
		query.WriteString(fmt.Sprintf(" OFFSET $%d", qb.argIndex))
		qb.args = append(qb.args, qb.offsetVal)
		qb.argIndex++
	} else if qb.offsetVal > 0 {
		// If only OFFSET is set (no LIMIT), add it
		query.WriteString(fmt.Sprintf(" OFFSET $%d", qb.argIndex))
		qb.args = append(qb.args, qb.offsetVal)
		qb.argIndex++
	}

	return query.String(), qb.args
}
