package server

import (
	"context"
	"fmt"

	"github.com/kooshapari/tracertm-backend/internal/services"
)

type branchRepoAdapter struct {
	repo services.BranchRepository
}

func (a *branchRepoAdapter) Create(ctx context.Context, branch interface{}) error {
	branchTyped, ok := branch.(*services.VersionBranch)
	if !ok {
		return fmt.Errorf("expected *services.VersionBranch, got %T", branch)
	}
	return a.repo.Create(ctx, branchTyped)
}

func (a *branchRepoAdapter) GetByID(ctx context.Context, id string) (interface{}, error) {
	return a.repo.GetByID(ctx, id)
}

func (a *branchRepoAdapter) ListByProject(ctx context.Context, projectID string) ([]interface{}, error) {
	branches, err := a.repo.ListByProject(ctx, projectID)
	if err != nil {
		return nil, err
	}
	result := make([]interface{}, len(branches))
	for i, b := range branches {
		result[i] = b
	}
	return result, nil
}

func (a *branchRepoAdapter) Update(ctx context.Context, branch interface{}) error {
	branchTyped, ok := branch.(*services.VersionBranch)
	if !ok {
		return fmt.Errorf("expected *services.VersionBranch, got %T", branch)
	}
	return a.repo.Update(ctx, branchTyped)
}

func (a *branchRepoAdapter) Delete(ctx context.Context, id string) error {
	return a.repo.Delete(ctx, id)
}

type versionRepoAdapter struct {
	repo services.VersionRepository
}

func (a *versionRepoAdapter) Create(ctx context.Context, version interface{}) error {
	versionTyped, ok := version.(*services.Version)
	if !ok {
		return fmt.Errorf("expected *services.Version, got %T", version)
	}
	return a.repo.Create(ctx, versionTyped)
}

func (a *versionRepoAdapter) GetByID(ctx context.Context, id string) (interface{}, error) {
	return a.repo.GetByID(ctx, id)
}

func (a *versionRepoAdapter) ListByBranch(ctx context.Context, branchID string) ([]interface{}, error) {
	versions, err := a.repo.ListByBranch(ctx, branchID)
	if err != nil {
		return nil, err
	}
	result := make([]interface{}, len(versions))
	for i, v := range versions {
		result[i] = v
	}
	return result, nil
}

func (a *versionRepoAdapter) Update(ctx context.Context, version interface{}) error {
	versionTyped, ok := version.(*services.Version)
	if !ok {
		return fmt.Errorf("expected *services.Version, got %T", version)
	}
	return a.repo.Update(ctx, versionTyped)
}

func (a *versionRepoAdapter) Delete(ctx context.Context, id string) error {
	return a.repo.Delete(ctx, id)
}

type itemVersionRepoAdapter struct {
	repo services.ItemVersionRepository
}

func (a *itemVersionRepoAdapter) Create(ctx context.Context, snapshot interface{}) error {
	snapshotTyped, ok := snapshot.(*services.ItemVersionSnapshot)
	if !ok {
		return fmt.Errorf("expected *services.ItemVersionSnapshot, got %T", snapshot)
	}
	return a.repo.Create(ctx, snapshotTyped)
}

func (a *itemVersionRepoAdapter) GetByItemAndVersion(ctx context.Context, itemID, versionID string) (interface{}, error) {
	return a.repo.GetByItemAndVersion(ctx, itemID, versionID)
}

func (a *itemVersionRepoAdapter) GetHistory(ctx context.Context, itemID, branchID string) ([]interface{}, error) {
	snapshots, err := a.repo.GetByItemAndBranch(ctx, itemID, branchID)
	if err != nil {
		return nil, err
	}
	result := make([]interface{}, len(snapshots))
	for i, s := range snapshots {
		result[i] = s
	}
	return result, nil
}

func (a *itemVersionRepoAdapter) Update(ctx context.Context, snapshot interface{}) error {
	snapshotTyped, ok := snapshot.(*services.ItemVersionSnapshot)
	if !ok {
		return fmt.Errorf("expected *services.ItemVersionSnapshot, got %T", snapshot)
	}
	return a.repo.Update(ctx, snapshotTyped)
}

func (a *itemVersionRepoAdapter) Delete(ctx context.Context, id string) error {
	return a.repo.Delete(ctx, id)
}

func (a *itemVersionRepoAdapter) GetByID(ctx context.Context, id string) (interface{}, error) {
	return a.repo.GetByID(ctx, id)
}

type altRepoAdapter struct {
	repo services.AlternativeRepository
}

func (a *altRepoAdapter) Create(ctx context.Context, alt interface{}) error {
	altTyped, ok := alt.(*services.ItemAlternative)
	if !ok {
		return fmt.Errorf("expected *services.ItemAlternative, got %T", alt)
	}
	return a.repo.Create(ctx, altTyped)
}

func (a *altRepoAdapter) GetByID(ctx context.Context, id string) (interface{}, error) {
	return a.repo.GetByID(ctx, id)
}

func (a *altRepoAdapter) ListByBase(ctx context.Context, baseItemID string) ([]interface{}, error) {
	alts, err := a.repo.ListByBase(ctx, baseItemID)
	if err != nil {
		return nil, err
	}
	result := make([]interface{}, len(alts))
	for i, alt := range alts {
		result[i] = alt
	}
	return result, nil
}

func (a *altRepoAdapter) Update(ctx context.Context, alt interface{}) error {
	altTyped, ok := alt.(*services.ItemAlternative)
	if !ok {
		return fmt.Errorf("expected *services.ItemAlternative, got %T", alt)
	}
	return a.repo.Update(ctx, altTyped)
}

func (a *altRepoAdapter) Delete(ctx context.Context, id string) error {
	return a.repo.Delete(ctx, id)
}

type mergeRepoAdapter struct {
	repo services.MergeRepository
}

func (a *mergeRepoAdapter) Create(ctx context.Context, mr interface{}) error {
	mrTyped, ok := mr.(*services.MergeRequest)
	if !ok {
		return fmt.Errorf("expected *services.MergeRequest, got %T", mr)
	}
	return a.repo.Create(ctx, mrTyped)
}

func (a *mergeRepoAdapter) GetByID(ctx context.Context, id string) (interface{}, error) {
	return a.repo.GetByID(ctx, id)
}

func (a *mergeRepoAdapter) ListByProject(ctx context.Context, projectID string, status string) ([]interface{}, error) {
	mrs, err := a.repo.ListByProject(ctx, projectID, status)
	if err != nil {
		return nil, err
	}
	result := make([]interface{}, len(mrs))
	for i, mr := range mrs {
		result[i] = mr
	}
	return result, nil
}

func (a *mergeRepoAdapter) Update(ctx context.Context, mr interface{}) error {
	mrTyped, ok := mr.(*services.MergeRequest)
	if !ok {
		return fmt.Errorf("expected *services.MergeRequest, got %T", mr)
	}
	return a.repo.Update(ctx, mrTyped)
}

func (a *mergeRepoAdapter) Delete(ctx context.Context, id string) error {
	return a.repo.Delete(ctx, id)
}
