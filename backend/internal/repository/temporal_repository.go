package repository

import (
	"context"
)

// BranchRepository handles version branch data access
// Note: Types moved to services package to avoid import cycle
type BranchRepository interface {
	Create(ctx context.Context, branch interface{}) error
	GetByID(ctx context.Context, id string) (interface{}, error)
	ListByProject(ctx context.Context, projectID string) ([]interface{}, error)
	Update(ctx context.Context, branch interface{}) error
	Delete(ctx context.Context, id string) error
}

// VersionRepository handles version data access
type VersionRepository interface {
	Create(ctx context.Context, version interface{}) error
	GetByID(ctx context.Context, id string) (interface{}, error)
	ListByBranch(ctx context.Context, branchID string) ([]interface{}, error)
	Update(ctx context.Context, version interface{}) error
	Delete(ctx context.Context, id string) error
}

// ItemVersionRepository handles item version mapping data access
type ItemVersionRepository interface {
	Create(ctx context.Context, snapshot interface{}) error
	GetByItemAndVersion(ctx context.Context, itemID, versionID string) (interface{}, error)
	GetHistory(ctx context.Context, itemID, branchID string) ([]interface{}, error)
	Update(ctx context.Context, snapshot interface{}) error
	Delete(ctx context.Context, id string) error
}

// AlternativeRepository handles item alternative data access
type AlternativeRepository interface {
	Create(ctx context.Context, alt interface{}) error
	GetByID(ctx context.Context, id string) (interface{}, error)
	ListByBase(ctx context.Context, baseItemID string) ([]interface{}, error)
	Update(ctx context.Context, alt interface{}) error
	Delete(ctx context.Context, id string) error
}

// MergeRepository handles merge request data access
type MergeRepository interface {
	Create(ctx context.Context, mr interface{}) error
	GetByID(ctx context.Context, id string) (interface{}, error)
	ListByProject(ctx context.Context, projectID string, status string) ([]interface{}, error)
	Update(ctx context.Context, mr interface{}) error
	Delete(ctx context.Context, id string) error
}
