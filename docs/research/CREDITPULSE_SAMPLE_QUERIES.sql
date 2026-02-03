-- CreditPulse Mock Data - Sample Queries
-- These queries demonstrate how to work with the loaded data

-- ============================================
-- 1. PROJECT & OVERVIEW QUERIES
-- ============================================

-- Get project details
SELECT * FROM projects WHERE name = 'CreditPulse - Personal Finance Platform';

-- Count items by type
SELECT item_type, COUNT(*) as count, 
       SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done,
       SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
       SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
GROUP BY item_type
ORDER BY item_type;

-- ============================================
-- 2. REQUIREMENTS QUERIES
-- ============================================

-- List all critical requirements
SELECT id, title, status, priority, owner
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'requirement'
  AND priority = 'critical'
ORDER BY title;

-- Get requirements by status
SELECT status, COUNT(*) as count
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'requirement'
GROUP BY status;

-- Find requirements with no assigned features
SELECT r.id, r.title, COUNT(f.id) as feature_count
FROM items r
LEFT JOIN items f ON r.id = f.parent_id AND f.item_type = 'feature'
WHERE r.project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND r.item_type = 'requirement'
GROUP BY r.id, r.title
HAVING COUNT(f.id) = 0
ORDER BY r.title;

-- ============================================
-- 3. FEATURES QUERIES
-- ============================================

-- List features by epic
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.epic')) as epic,
    COUNT(*) as feature_count,
    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'feature'
GROUP BY epic
ORDER BY epic;

-- Get all features for credit monitoring
SELECT id, title, status, priority, 
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.effort')) as effort_points
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'feature'
  AND JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.epic')) = 'credit_monitoring'
ORDER BY title;

-- Features by completion percentage
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.epic')) as epic,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done,
    ROUND(100 * SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) / COUNT(*), 1) as completion_percent
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'feature'
GROUP BY epic
ORDER BY completion_percent DESC;

-- ============================================
-- 4. USER STORIES QUERIES
-- ============================================

-- List all user stories with story points
SELECT id, title, status, priority,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.story_points')) as points,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.acceptance_criteria')) as criteria
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'user_story'
ORDER BY title;

-- User stories by status and points
SELECT status, 
       SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.story_points')) AS INT)) as total_points,
       COUNT(*) as story_count
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'user_story'
GROUP BY status
ORDER BY status;

-- ============================================
-- 5. TASK QUERIES
-- ============================================

-- All tasks with time estimates
SELECT id, title, status, priority,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.time_estimate')) as time_estimate,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.tags')) as tags
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'task'
ORDER BY priority DESC, status;

-- Tasks by owner
SELECT owner, COUNT(*) as task_count,
       SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
       SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
       SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as backlog
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'task'
GROUP BY owner
ORDER BY task_count DESC;

-- ============================================
-- 6. TEST QUERIES
-- ============================================

-- Test coverage summary
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.type')) as test_type,
    COUNT(*) as count,
    ROUND(AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.coverage')) AS INT)), 1) as avg_coverage
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'test'
GROUP BY test_type
ORDER BY count DESC;

-- Low coverage tests
SELECT id, title, status,
       CAST(JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.coverage')) AS INT) as coverage
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'test'
  AND CAST(JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.coverage')) AS INT) < 90
ORDER BY coverage;

-- ============================================
-- 7. API QUERIES
-- ============================================

-- All APIs with response times
SELECT id, title, status,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.method')) as method,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.auth')) as auth,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.response_time')) as response_time
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'api'
ORDER BY title;

-- Slow APIs (over 2 seconds)
SELECT title, 
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.method')) as method,
       JSON_UNQUOTE(JSON_EXTRACT(item_metadata, '$.response_time')) as response_time
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND item_type = 'api'
  AND JSON_EXTRACT(item_metadata, '$.response_time') LIKE '%s%'
ORDER BY title;

-- ============================================
-- 8. TEAM WORKLOAD QUERIES
-- ============================================

-- Items assigned per team member
SELECT owner, item_type, status, COUNT(*) as count
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
GROUP BY owner, item_type, status
ORDER BY owner, item_type;

-- Total items per person
SELECT owner, COUNT(*) as total_items,
       SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
       SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as active,
       SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as backlog
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
GROUP BY owner
ORDER BY total_items DESC;

-- ============================================
-- 9. DEPENDENCY QUERIES
-- ============================================

-- Items with the most dependencies
SELECT 
    source.id, source.title as source_title, source.item_type,
    COUNT(l.id) as dependency_count
FROM items source
LEFT JOIN links l ON source.id = l.source_item_id
WHERE source.project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
GROUP BY source.id, source.title, source.item_type
HAVING COUNT(l.id) > 0
ORDER BY dependency_count DESC
LIMIT 10;

-- Items that are blocked (depend on todos)
SELECT 
    source.id, source.title as blocked_item,
    target.title as blocking_item,
    target.status as blocker_status
FROM items source
JOIN links l ON source.id = l.source_item_id
JOIN items target ON l.target_item_id = target.id
WHERE source.project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND l.link_type = 'depends_on'
  AND target.status = 'todo'
ORDER BY source.title;

-- ============================================
-- 10. PRIORITY & STATUS ANALYSIS
-- ============================================

-- Critical items still in backlog
SELECT item_type, status, COUNT(*) as count
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
  AND priority = 'critical'
GROUP BY item_type, status
ORDER BY item_type;

-- Completion rate by priority
SELECT priority,
       COUNT(*) as total,
       SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
       ROUND(100 * SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) / COUNT(*), 1) as completion_percent
FROM items
WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')
GROUP BY priority
ORDER BY priority;

-- Overall project health
SELECT 
    (SELECT COUNT(*) FROM items WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform') AND status = 'done') as completed_items,
    (SELECT COUNT(*) FROM items WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform') AND status = 'in_progress') as active_items,
    (SELECT COUNT(*) FROM items WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform') AND status = 'todo') as backlog_items,
    (SELECT COUNT(*) FROM items WHERE project_id = (SELECT id FROM projects WHERE name = 'CreditPulse - Personal Finance Platform')) as total_items;

