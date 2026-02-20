-- sqlc queries for TraceRTM
-- Run: sqlc generate

-- Projects
-- name: CreateProject :one
INSERT INTO projects (name, description, metadata)
VALUES ($1, $2, $3)
RETURNING id, name, description, metadata, created_at, updated_at, deleted_at;

-- name: GetProject :one
SELECT id, name, description, metadata, created_at, updated_at, deleted_at
FROM projects
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListProjects :many
SELECT id, name, description, metadata, created_at, updated_at, deleted_at
FROM projects
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: UpdateProject :one
UPDATE projects
SET name = $2, description = $3, metadata = $4, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, name, description, metadata, created_at, updated_at, deleted_at;

-- name: DeleteProject :exec
UPDATE projects SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Items
-- name: CreateItem :one
INSERT INTO items (project_id, title, description, type, status, priority, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at;

-- name: GetItem :one
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListItemsByProject :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- name: ListItemsByProjectAndType :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE project_id = $1 AND type = $2 AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $3 OFFSET $4;

-- name: UpdateItem :one
UPDATE items
SET title = $2, description = $3, type = $4, status = $5, priority = $6, metadata = $7, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at;

-- name: DeleteItem :exec
UPDATE items SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Links
-- name: CreateLink :one
INSERT INTO links (source_id, target_id, type, metadata)
VALUES ($1, $2, $3, $4)
RETURNING id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at;

-- name: GetLink :one
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListLinksBySource :many
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE source_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- name: ListLinksByTarget :many
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE target_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- name: UpdateLink :one
UPDATE links
SET
  type = $2,
  metadata = $3,
  updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at;

-- name: DeleteLink :exec
UPDATE links SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Agents
-- name: CreateAgent :one
INSERT INTO agents (project_id, name, status, metadata)
VALUES ($1, $2, $3, $4)
RETURNING id, project_id, name, status, metadata, last_activity_at, created_at, updated_at, deleted_at;

-- name: GetAgent :one
SELECT id, project_id, name, status, metadata, last_activity_at, created_at, updated_at, deleted_at
FROM agents
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListAgentsByProject :many
SELECT id, project_id, name, status, metadata, last_activity_at, created_at, updated_at, deleted_at
FROM agents
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- name: UpdateAgent :one
UPDATE agents
SET name = $2, status = $3, metadata = $4, last_activity_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, project_id, name, status, metadata, last_activity_at, created_at, updated_at, deleted_at;

-- name: DeleteAgent :exec
UPDATE agents SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Graph Queries (Recursive CTEs for traversal)
-- name: GetDescendants :many
WITH RECURSIVE descendants AS (
  SELECT links.id, links.source_id, links.target_id, links.type, 0 as depth
  FROM links
  WHERE links.source_id = $1 AND links.deleted_at IS NULL

  UNION ALL

  SELECT l.id, l.source_id, l.target_id, l.type, d.depth + 1
  FROM links l
  INNER JOIN descendants d ON l.source_id = d.target_id
  WHERE l.deleted_at IS NULL AND d.depth < 10
)
SELECT descendants.target_id as item_id, descendants.type as link_type, descendants.depth
FROM descendants
ORDER BY descendants.depth, descendants.item_id;

-- name: GetAncestors :many
WITH RECURSIVE ancestors AS (
  SELECT links.id, links.source_id, links.target_id, links.type, 0 as depth
  FROM links
  WHERE links.target_id = $1 AND links.deleted_at IS NULL

  UNION ALL

  SELECT l.id, l.source_id, l.target_id, l.type, a.depth + 1
  FROM links l
  INNER JOIN ancestors a ON l.target_id = a.source_id
  WHERE l.deleted_at IS NULL AND a.depth < 10
)
SELECT ancestors.source_id as item_id, ancestors.type as link_type, ancestors.depth
FROM ancestors
ORDER BY ancestors.depth, ancestors.item_id;

-- name: GetImpactAnalysis :many
WITH RECURSIVE impact AS (
  SELECT links.id, links.source_id, links.target_id, links.type, 0 as depth, ARRAY[links.target_id] as path
  FROM links
  WHERE links.source_id = $1 AND links.deleted_at IS NULL

  UNION ALL

  SELECT l.id, l.source_id, l.target_id, l.type, i.depth + 1, i.path || l.target_id
  FROM links l
  INNER JOIN impact i ON l.source_id = i.target_id
  WHERE l.deleted_at IS NULL AND i.depth < 10 AND NOT l.target_id = ANY(i.path)
)
SELECT impact.target_id as item_id, impact.type as link_type, impact.depth
FROM impact
ORDER BY impact.depth, impact.item_id;

-- Full-Text Search Queries
-- name: SearchItems :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE project_id = $1
  AND deleted_at IS NULL
  AND search_vector @@ plainto_tsquery('english', $2)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', $2)) DESC
LIMIT $3 OFFSET $4;

-- name: SearchItemsByType :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE project_id = $1
  AND type = $2
  AND deleted_at IS NULL
  AND search_vector @@ plainto_tsquery('english', $3)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', $3)) DESC
LIMIT $4 OFFSET $5;

-- Vector Search Queries (Semantic Search)
-- name: SearchItemsByEmbedding :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at,
       1 - (embedding <=> $2::vector) as similarity
FROM items
WHERE project_id = $1
  AND deleted_at IS NULL
  AND embedding IS NOT NULL
ORDER BY embedding <=> $2::vector
LIMIT $3;

-- Graph Queries - Additional operations
-- name: ListItemsByProjectIDs :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- name: ListItemsByIDs :many
SELECT id, project_id, title, description, type, status, priority, metadata, created_at, updated_at, deleted_at
FROM items
WHERE id = ANY($1::uuid[]) AND deleted_at IS NULL;

-- name: ListLinksBySourceIDs :many
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE source_id = ANY($1::uuid[]) AND deleted_at IS NULL;

-- name: ListLinksByTargetIDs :many
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE target_id = ANY($1::uuid[]) AND deleted_at IS NULL;

-- name: ListLinksBetweenItems :many
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE source_id = ANY($1::uuid[]) AND target_id = ANY($1::uuid[]) AND deleted_at IS NULL;

-- name: GetOrphanItems :many
SELECT i.id, i.project_id, i.title, i.description, i.type, i.status, i.priority, i.metadata, i.created_at, i.updated_at, i.deleted_at
FROM items i
WHERE i.project_id = $1
  AND i.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM links l1 WHERE l1.source_id = i.id AND l1.deleted_at IS NULL
  )
  AND NOT EXISTS (
    SELECT 1 FROM links l2 WHERE l2.target_id = i.id AND l2.deleted_at IS NULL
  )
ORDER BY i.created_at DESC;

-- name: GetLinkBySourceAndTarget :one
SELECT id, source_id, target_id, type, metadata, created_at, updated_at, deleted_at
FROM links
WHERE source_id = $1 AND target_id = $2 AND deleted_at IS NULL
LIMIT 1;

-- Profiles
-- name: CreateProfile :one
INSERT INTO profiles (workos_user_id, workos_org_id, email, full_name, avatar_url, metadata)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at;

-- name: GetProfile :one
SELECT id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at
FROM profiles
WHERE id = $1 AND deleted_at IS NULL;

-- name: GetProfileByWorkOSUserID :one
SELECT id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at
FROM profiles
WHERE workos_user_id = $1 AND deleted_at IS NULL;

-- name: GetProfileByEmail :one
SELECT id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at
FROM profiles
WHERE email = $1 AND deleted_at IS NULL;

-- name: ListProfiles :many
SELECT id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at
FROM profiles
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: UpdateProfile :one
UPDATE profiles
SET full_name = $2, avatar_url = $3, metadata = $4, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, auth_id, workos_user_id, workos_org_id, workos_ids, email, full_name, avatar_url, metadata, created_at, updated_at, deleted_at;

-- name: DeleteProfile :exec
UPDATE profiles SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Milestones
-- name: CreateMilestone :one
INSERT INTO milestones (project_id, parent_id, name, slug, description, objective, start_date, target_date, status, health, owner_id, tags, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
RETURNING id, project_id, parent_id, name, slug, description, objective, start_date, target_date, actual_date, status, health, risk_score, risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at;

-- name: GetMilestone :one
SELECT id, project_id, parent_id, name, slug, description, objective, start_date, target_date, actual_date, status, health, risk_score, risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at
FROM milestones
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListMilestonesByProject :many
SELECT id, project_id, parent_id, name, slug, description, objective, start_date, target_date, actual_date, status, health, risk_score, risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at
FROM milestones
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY target_date ASC;

-- name: UpdateMilestone :one
UPDATE milestones
SET name = $2, description = $3, objective = $4, start_date = $5, target_date = $6, status = $7, health = $8, metadata = $9, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, project_id, parent_id, name, slug, description, objective, start_date, target_date, actual_date, status, health, risk_score, risk_factors, owner_id, tags, metadata, created_at, updated_at, deleted_at;

-- name: DeleteMilestone :exec
UPDATE milestones SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Milestone Items (join table)
-- name: AddItemToMilestone :exec
INSERT INTO milestone_items (milestone_id, item_id) VALUES ($1, $2);

-- name: RemoveItemFromMilestone :exec
DELETE FROM milestone_items WHERE milestone_id = $1 AND item_id = $2;

-- name: ListItemsByMilestone :many
SELECT i.id, i.project_id, i.title, i.description, i.type, i.status, i.priority, i.metadata, i.created_at, i.updated_at, i.deleted_at
FROM items i
INNER JOIN milestone_items mi ON i.id = mi.item_id
WHERE mi.milestone_id = $1 AND i.deleted_at IS NULL
ORDER BY i.created_at DESC;

-- name: ListMilestonesByItem :many
SELECT m.id, m.project_id, m.parent_id, m.name, m.slug, m.description, m.objective, m.start_date, m.target_date, m.actual_date, m.status, m.health, m.risk_score, m.risk_factors, m.owner_id, m.tags, m.metadata, m.created_at, m.updated_at, m.deleted_at
FROM milestones m
INNER JOIN milestone_items mi ON m.id = mi.milestone_id
WHERE mi.item_id = $1 AND m.deleted_at IS NULL
ORDER BY m.target_date ASC;

-- Sprints
-- name: CreateSprint :one
INSERT INTO sprints (project_id, name, slug, goal, start_date, end_date, status, health, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
RETURNING id, project_id, name, slug, goal, start_date, end_date, status, health, planned_capacity, actual_capacity, planned_points, completed_points, remaining_points, added_points, removed_points, metadata, created_at, updated_at, completed_at, deleted_at;

-- name: GetSprint :one
SELECT id, project_id, name, slug, goal, start_date, end_date, status, health, planned_capacity, actual_capacity, planned_points, completed_points, remaining_points, added_points, removed_points, metadata, created_at, updated_at, completed_at, deleted_at
FROM sprints
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListSprintsByProject :many
SELECT id, project_id, name, slug, goal, start_date, end_date, status, health, planned_capacity, actual_capacity, planned_points, completed_points, remaining_points, added_points, removed_points, metadata, created_at, updated_at, completed_at, deleted_at
FROM sprints
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY start_date DESC;

-- name: UpdateSprint :one
UPDATE sprints
SET name = $2, goal = $3, start_date = $4, end_date = $5, status = $6, health = $7, metadata = $8, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, project_id, name, slug, goal, start_date, end_date, status, health, planned_capacity, actual_capacity, planned_points, completed_points, remaining_points, added_points, removed_points, metadata, created_at, updated_at, completed_at, deleted_at;

-- name: DeleteSprint :exec
UPDATE sprints SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Sprint Items (join table)
-- name: AddItemToSprint :exec
INSERT INTO sprint_items (sprint_id, item_id) VALUES ($1, $2);

-- name: RemoveItemFromSprint :exec
DELETE FROM sprint_items WHERE sprint_id = $1 AND item_id = $2;

-- name: ListItemsBySprint :many
SELECT i.id, i.project_id, i.title, i.description, i.type, i.status, i.priority, i.metadata, i.created_at, i.updated_at, i.deleted_at
FROM items i
INNER JOIN sprint_items si ON i.id = si.item_id
WHERE si.sprint_id = $1 AND i.deleted_at IS NULL
ORDER BY i.created_at DESC;

-- Version Branches
-- name: CreateVersionBranch :one
INSERT INTO version_branches (project_id, name, slug, description, branch_type, parent_branch_id, base_version_id, status, is_default, is_protected, created_by, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
RETURNING id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id, status, is_default, is_protected, merged_at, merged_into, merged_by, version_count, item_count, metadata, created_by, created_at, updated_at;

-- name: GetVersionBranch :one
SELECT id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id, status, is_default, is_protected, merged_at, merged_into, merged_by, version_count, item_count, metadata, created_by, created_at, updated_at
FROM version_branches
WHERE id = $1;

-- name: ListVersionBranchesByProject :many
SELECT id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id, status, is_default, is_protected, merged_at, merged_into, merged_by, version_count, item_count, metadata, created_by, created_at, updated_at
FROM version_branches
WHERE project_id = $1
ORDER BY created_at DESC;

-- name: UpdateVersionBranch :one
UPDATE version_branches
SET name = $2, description = $3, status = $4, metadata = $5, updated_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING id, project_id, name, slug, description, branch_type, parent_branch_id, base_version_id, status, is_default, is_protected, merged_at, merged_into, merged_by, version_count, item_count, metadata, created_by, created_at, updated_at;

-- name: DeleteVersionBranch :exec
DELETE FROM version_branches WHERE id = $1;

-- Versions
-- name: CreateVersion :one
INSERT INTO versions (branch_id, project_id, version_number, parent_version_id, tag, message, status, created_by, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
RETURNING id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id, tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason, metadata, created_by, created_at;

-- name: GetVersion :one
SELECT id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id, tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason, metadata, created_by, created_at
FROM versions
WHERE id = $1;

-- name: ListVersionsByBranch :many
SELECT id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id, tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason, metadata, created_by, created_at
FROM versions
WHERE branch_id = $1
ORDER BY version_number DESC;

-- name: UpdateVersion :one
UPDATE versions
SET message = $2, status = $3, metadata = $4
WHERE id = $1
RETURNING id, branch_id, project_id, version_number, parent_version_id, snapshot_id, changeset_id, tag, message, item_count, change_count, status, approved_by, approved_at, rejection_reason, metadata, created_by, created_at;

-- name: DeleteVersion :exec
DELETE FROM versions WHERE id = $1;

-- Item Versions
-- name: CreateItemVersion :one
INSERT INTO item_versions (item_id, version_id, branch_id, project_id, state, lifecycle)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id, item_id, version_id, branch_id, project_id, state, lifecycle, introduced_in_version_id, last_modified_in_version_id, created_at;

-- name: GetItemVersion :one
SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle, introduced_in_version_id, last_modified_in_version_id, created_at
FROM item_versions
WHERE id = $1;

-- name: ListItemVersionsByItem :many
SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle, introduced_in_version_id, last_modified_in_version_id, created_at
FROM item_versions
WHERE item_id = $1
ORDER BY created_at DESC;

-- name: ListItemVersionsByVersion :many
SELECT id, item_id, version_id, branch_id, project_id, state, lifecycle, introduced_in_version_id, last_modified_in_version_id, created_at
FROM item_versions
WHERE version_id = $1
ORDER BY created_at DESC;

-- name: DeleteItemVersion :exec
DELETE FROM item_versions WHERE id = $1;

-- Documentation
-- name: CreateDocumentation :one
INSERT INTO documentation (project_id, title, slug, format, content, summary, parsed_structure, tags, source_url, file_path, metadata)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
RETURNING id, project_id, title, slug, format, content, summary, parsed_structure, tags, version, source_url, file_path, full_text_search, metadata, created_by, created_at, updated_at, deleted_at;

-- name: GetDocumentation :one
SELECT id, project_id, title, slug, format, content, summary, parsed_structure, tags, version, source_url, file_path, full_text_search, metadata, created_by, created_at, updated_at, deleted_at
FROM documentation
WHERE id = $1 AND deleted_at IS NULL;

-- name: ListDocumentationByProject :many
SELECT id, project_id, title, slug, format, content, summary, parsed_structure, tags, version, source_url, file_path, full_text_search, metadata, created_by, created_at, updated_at, deleted_at
FROM documentation
WHERE project_id = $1 AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- name: UpdateDocumentation :one
UPDATE documentation
SET title = $2, content = $3, summary = $4, parsed_structure = $5, tags = $6, metadata = $7, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, project_id, title, slug, format, content, summary, parsed_structure, tags, version, source_url, file_path, full_text_search, metadata, created_by, created_at, updated_at, deleted_at;

-- name: DeleteDocumentation :exec
UPDATE documentation SET deleted_at = CURRENT_TIMESTAMP WHERE id = $1;

-- Events
-- name: CreateEvent :one
INSERT INTO events (project_id, entity_type, entity_id, event_type, data, metadata, version, causation_id, correlation_id)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
RETURNING id, project_id, entity_type, entity_id, event_type, data, metadata, version, causation_id, correlation_id, created_at;

-- name: GetEvent :one
SELECT id, project_id, entity_type, entity_id, event_type, data, metadata, version, causation_id, correlation_id, created_at
FROM events
WHERE id = $1;

-- name: ListEventsByEntity :many
SELECT id, project_id, entity_type, entity_id, event_type, data, metadata, version, causation_id, correlation_id, created_at
FROM events
WHERE entity_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- name: ListEventsByProject :many
SELECT id, project_id, entity_type, entity_id, event_type, data, metadata, version, causation_id, correlation_id, created_at
FROM events
WHERE project_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- Progress Snapshots
-- name: CreateProgressSnapshot :one
INSERT INTO progress_snapshots (project_id, snapshot_date, metrics)
VALUES ($1, $2, $3)
RETURNING id, project_id, snapshot_date, metrics, created_at;

-- name: GetProgressSnapshot :one
SELECT id, project_id, snapshot_date, metrics, created_at
FROM progress_snapshots
WHERE id = $1;

-- name: ListProgressSnapshotsByProject :many
SELECT id, project_id, snapshot_date, metrics, created_at
FROM progress_snapshots
WHERE project_id = $1
ORDER BY snapshot_date DESC
LIMIT $2 OFFSET $3;

-- name: DeleteProgressSnapshot :exec
DELETE FROM progress_snapshots WHERE id = $1;

-- Velocity History
-- name: CreateVelocityHistory :one
INSERT INTO velocity_history (project_id, period_start, period_end, period_label, planned_points, completed_points, velocity)
VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING id, project_id, period_start, period_end, period_label, planned_points, completed_points, velocity, created_at;

-- name: GetVelocityHistory :one
SELECT id, project_id, period_start, period_end, period_label, planned_points, completed_points, velocity, created_at
FROM velocity_history
WHERE id = $1;

-- name: ListVelocityHistoryByProject :many
SELECT id, project_id, period_start, period_end, period_label, planned_points, completed_points, velocity, created_at
FROM velocity_history
WHERE project_id = $1
ORDER BY period_start DESC
LIMIT $2 OFFSET $3;

-- name: DeleteVelocityHistory :exec
DELETE FROM velocity_history WHERE id = $1;

-- Burndown Data
-- name: CreateBurndownData :one
INSERT INTO burndown_data (sprint_id, recorded_date, remaining_points, ideal_points, completed_points, added_points)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id, sprint_id, recorded_date, remaining_points, ideal_points, completed_points, added_points, created_at;

-- name: GetBurndownData :one
SELECT id, sprint_id, recorded_date, remaining_points, ideal_points, completed_points, added_points, created_at
FROM burndown_data
WHERE id = $1;

-- name: ListBurndownDataBySprint :many
SELECT id, sprint_id, recorded_date, remaining_points, ideal_points, completed_points, added_points, created_at
FROM burndown_data
WHERE sprint_id = $1
ORDER BY recorded_date ASC;

-- name: DeleteBurndownData :exec
DELETE FROM burndown_data WHERE id = $1;

-- Change Log
-- name: CreateChangeLog :one
INSERT INTO change_log (entity_type, entity_id, action, changes)
VALUES ($1, $2, $3, $4)
RETURNING id, entity_type, entity_id, action, changes, created_at;

-- name: GetChangeLog :one
SELECT id, entity_type, entity_id, action, changes, created_at
FROM change_log
WHERE id = $1;

-- name: ListChangeLogByEntity :many
SELECT id, entity_type, entity_id, action, changes, created_at
FROM change_log
WHERE entity_type = $1 AND entity_id = $2
ORDER BY created_at DESC
LIMIT $3 OFFSET $4;

-- Snapshots
-- name: CreateSnapshot :one
INSERT INTO snapshots (project_id, entity_type, entity_id, version, state)
VALUES ($1, $2, $3, $4, $5)
RETURNING id, project_id, entity_type, entity_id, version, state, created_at;

-- name: GetSnapshot :one
SELECT id, project_id, entity_type, entity_id, version, state, created_at
FROM snapshots
WHERE id = $1;

-- name: GetSnapshotByEntityVersion :one
SELECT id, project_id, entity_type, entity_id, version, state, created_at
FROM snapshots
WHERE entity_id = $1 AND version = $2;

-- name: ListSnapshotsByEntity :many
SELECT id, project_id, entity_type, entity_id, version, state, created_at
FROM snapshots
WHERE entity_id = $1
ORDER BY version DESC
LIMIT $2 OFFSET $3;

-- Merge Requests
-- name: CreateMergeRequest :one
INSERT INTO merge_requests (project_id, source_branch_id, target_branch_id, source_version_id, title, description, created_by)
VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id, status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at, merged_at, merged_by, closed_at, updated_at;

-- name: GetMergeRequest :one
SELECT id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id, status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at, merged_at, merged_by, closed_at, updated_at
FROM merge_requests
WHERE id = $1;

-- name: ListMergeRequestsByProject :many
SELECT id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id, status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at, merged_at, merged_by, closed_at, updated_at
FROM merge_requests
WHERE project_id = $1
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;

-- name: UpdateMergeRequest :one
UPDATE merge_requests
SET status = $2, title = $3, description = $4, updated_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING id, project_id, source_branch_id, target_branch_id, source_version_id, base_version_id, status, title, description, diff, conflicts, reviewers, approved_by, created_by, created_at, merged_at, merged_by, closed_at, updated_at;

-- name: DeleteMergeRequest :exec
DELETE FROM merge_requests WHERE id = $1;

-- Item Alternatives
-- name: CreateItemAlternative :one
INSERT INTO item_alternatives (project_id, base_item_id, alternative_item_id, relationship, description, metrics)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id, project_id, base_item_id, alternative_item_id, relationship, description, is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at;

-- name: GetItemAlternative :one
SELECT id, project_id, base_item_id, alternative_item_id, relationship, description, is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at
FROM item_alternatives
WHERE id = $1;

-- name: ListItemAlternativesByBase :many
SELECT id, project_id, base_item_id, alternative_item_id, relationship, description, is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at
FROM item_alternatives
WHERE base_item_id = $1
ORDER BY created_at DESC;

-- name: UpdateItemAlternative :one
UPDATE item_alternatives
SET description = $2, is_chosen = $3, metrics = $4, updated_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING id, project_id, base_item_id, alternative_item_id, relationship, description, is_chosen, chosen_at, chosen_by, chosen_reason, metrics, created_at, updated_at;

-- name: DeleteItemAlternative :exec
DELETE FROM item_alternatives WHERE id = $1;

