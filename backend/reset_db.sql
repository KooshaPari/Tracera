-- Drop all existing tables to start fresh
DROP TABLE IF EXISTS snapshots CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS change_log CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS links CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS schema_migrations CASCADE;

-- Drop all indexes
DROP INDEX IF EXISTS idx_snapshots_entity_version;
DROP INDEX IF EXISTS idx_snapshots_project_id;
DROP INDEX IF EXISTS idx_snapshots_entity_id;
DROP INDEX IF EXISTS idx_events_causation_id;
DROP INDEX IF EXISTS idx_events_correlation_id;
DROP INDEX IF EXISTS idx_events_entity_version;
DROP INDEX IF EXISTS idx_events_created_at;
DROP INDEX IF EXISTS idx_events_project_id;
DROP INDEX IF EXISTS idx_events_entity_id;
DROP INDEX IF EXISTS idx_change_log_created_at;
DROP INDEX IF EXISTS idx_change_log_entity;
DROP INDEX IF EXISTS idx_agents_status;
DROP INDEX IF EXISTS idx_agents_project_id;
DROP INDEX IF EXISTS idx_links_link_type;
DROP INDEX IF EXISTS idx_links_target_id;
DROP INDEX IF EXISTS idx_links_source_id;
DROP INDEX IF EXISTS idx_items_status;
DROP INDEX IF EXISTS idx_items_project_id;
DROP INDEX IF EXISTS idx_projects_profile_id;
DROP INDEX IF EXISTS idx_email;
DROP INDEX IF EXISTS idx_workos_id;

SELECT 'Database reset complete' as status;
