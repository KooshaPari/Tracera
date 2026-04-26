package valueobjects

// Pagination represents pagination parameters
type Pagination struct {
	Page     int
	PageSize int
}

// DefaultPagination returns default pagination values
func DefaultPagination() Pagination {
	return Pagination{
		Page:     1,
		PageSize: 20,
	}
}

// Offset calculates the offset for database queries
func (p Pagination) Offset() int {
	return (p.Page - 1) * p.PageSize
}

// Limit returns the page size
func (p Pagination) Limit() int {
	if p.PageSize > 100 {
		return 100 // Max page size
	}
	return p.PageSize
}
