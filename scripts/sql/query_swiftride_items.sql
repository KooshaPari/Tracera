-- SwiftRide Product Layer Exploration Queries
-- Project: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e

-- 1. Overview: Item counts by type
SELECT
  type,
  COUNT(*) as count,
  MIN(priority) as min_priority,
  MAX(priority) as max_priority,
  ROUND(AVG(priority)::numeric, 2) as avg_priority
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY type
ORDER BY count DESC;

-- 2. Top 10 Strategic Initiatives (by priority)
SELECT
  title,
  priority,
  LEFT(description, 80) || '...' as description_preview
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'initiative'
ORDER BY priority DESC, title
LIMIT 10;

-- 3. Epics per Initiative (with counts)
SELECT
  i.title as initiative,
  COUNT(DISTINCT e.id) as epic_count,
  i.priority
FROM items i
LEFT JOIN links l ON i.id = l.target_id AND l.link_type = 'implements'
LEFT JOIN items e ON l.source_id = e.id AND e.type = 'epic'
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND i.type = 'initiative'
GROUP BY i.id, i.title, i.priority
ORDER BY i.priority DESC, epic_count DESC
LIMIT 15;

-- 4. Features per Epic (top 10 epics by feature count)
SELECT
  e.title as epic,
  COUNT(DISTINCT f.id) as feature_count,
  e.priority
FROM items e
LEFT JOIN links l ON e.id = l.target_id AND l.link_type = 'implements'
LEFT JOIN items f ON l.source_id = f.id AND f.type = 'feature'
WHERE e.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND e.type = 'epic'
GROUP BY e.id, e.title, e.priority
ORDER BY feature_count DESC
LIMIT 10;

-- 5. User Stories per Feature (sample of 10)
SELECT
  f.title as feature,
  COUNT(DISTINCT us.id) as story_count
FROM items f
LEFT JOIN links l ON f.id = l.target_id AND l.link_type = 'implements'
LEFT JOIN items us ON l.source_id = us.id AND us.type = 'user_story'
WHERE f.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND f.type = 'feature'
GROUP BY f.id, f.title
ORDER BY story_count DESC
LIMIT 10;

-- 6. Tasks per User Story (distribution)
SELECT
  task_count,
  COUNT(*) as story_count
FROM (
  SELECT
    us.id,
    COUNT(DISTINCT t.id) as task_count
  FROM items us
  LEFT JOIN links l ON us.id = l.target_id AND l.link_type = 'implements'
  LEFT JOIN items t ON l.source_id = t.id AND t.type = 'task'
  WHERE us.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
    AND us.type = 'user_story'
  GROUP BY us.id
) task_dist
GROUP BY task_count
ORDER BY task_count;

-- 7. Link Type Distribution
SELECT
  link_type,
  COUNT(*) as count
FROM links l
JOIN items i ON l.source_id = i.id
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY link_type
ORDER BY count DESC;

-- 8. Complete Hierarchy: Initiative → Epic → Feature → Story → Task (sample)
SELECT
  i.title as initiative,
  e.title as epic,
  f.title as feature,
  us.title as user_story,
  t.title as task
FROM items i
JOIN links l1 ON i.id = l1.target_id AND l1.link_type = 'implements'
JOIN items e ON l1.source_id = e.id AND e.type = 'epic'
JOIN links l2 ON e.id = l2.target_id AND l2.link_type = 'implements'
JOIN items f ON l2.source_id = f.id AND f.type = 'feature'
JOIN links l3 ON f.id = l3.target_id AND l3.link_type = 'implements'
JOIN items us ON l3.source_id = us.id AND us.type = 'user_story'
JOIN links l4 ON us.id = l4.target_id AND l4.link_type = 'implements'
JOIN items t ON l4.source_id = t.id AND t.type = 'task'
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND i.type = 'initiative'
ORDER BY i.priority DESC, e.priority DESC, f.priority DESC
LIMIT 20;

-- 9. Capabilities and their supporting epics
SELECT
  c.title as capability,
  STRING_AGG(e.title, '; ' ORDER BY e.title) as supported_epics,
  COUNT(DISTINCT e.id) as epic_count
FROM items c
JOIN links l ON c.id = l.source_id AND l.link_type = 'supports'
JOIN items e ON l.target_id = e.id AND e.type = 'epic'
WHERE c.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND c.type = 'capability'
GROUP BY c.id, c.title
ORDER BY epic_count DESC
LIMIT 15;

-- 10. Use Cases and validated features
SELECT
  uc.title as use_case,
  STRING_AGG(f.title, '; ' ORDER BY f.title) as validated_features,
  COUNT(DISTINCT f.id) as feature_count
FROM items uc
JOIN links l ON uc.id = l.source_id AND l.link_type = 'validates'
JOIN items f ON l.target_id = f.id AND f.type = 'feature'
WHERE uc.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND uc.type = 'use_case'
GROUP BY uc.id, uc.title
ORDER BY feature_count DESC
LIMIT 15;

-- 11. Priority distribution across all item types
SELECT
  priority,
  COUNT(CASE WHEN type = 'initiative' THEN 1 END) as initiatives,
  COUNT(CASE WHEN type = 'epic' THEN 1 END) as epics,
  COUNT(CASE WHEN type = 'capability' THEN 1 END) as capabilities,
  COUNT(CASE WHEN type = 'feature' THEN 1 END) as features,
  COUNT(CASE WHEN type = 'user_story' THEN 1 END) as user_stories,
  COUNT(CASE WHEN type = 'use_case' THEN 1 END) as use_cases,
  COUNT(*) as total
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type IN ('initiative', 'epic', 'capability', 'feature', 'user_story', 'use_case')
GROUP BY priority
ORDER BY priority DESC;

-- 12. Sample user stories with acceptance criteria
SELECT
  us.title as user_story,
  LEFT(us.description, 100) as story_description,
  ac.title as acceptance_criterion,
  us.priority
FROM items us
LEFT JOIN links l ON us.id = l.target_id AND l.link_type = 'validates'
LEFT JOIN items ac ON l.source_id = ac.id AND ac.type = 'acceptance_criteria'
WHERE us.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND us.type = 'user_story'
  AND ac.id IS NOT NULL
ORDER BY us.priority DESC, us.title
LIMIT 20;

-- 13. Traceability depth analysis
WITH RECURSIVE trace AS (
  -- Start with tasks
  SELECT
    id,
    type,
    title,
    1 as depth,
    id::text as path
  FROM items
  WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
    AND type = 'task'

  UNION ALL

  -- Follow implements links upward
  SELECT
    i.id,
    i.type,
    i.title,
    t.depth + 1,
    i.id::text || ' -> ' || t.path
  FROM items i
  JOIN links l ON i.id = l.target_id AND l.link_type = 'implements'
  JOIN trace t ON l.source_id = t.id
  WHERE t.depth < 10  -- Prevent infinite recursion
)
SELECT
  MAX(depth) as max_trace_depth,
  AVG(depth) as avg_trace_depth,
  MIN(depth) as min_trace_depth
FROM trace
WHERE type = 'initiative';

-- 14. Items without links (orphaned items - should be minimal)
SELECT
  type,
  COUNT(*) as orphaned_count
FROM items i
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type IN ('initiative', 'epic', 'capability', 'feature', 'user_story', 'use_case', 'acceptance_criteria', 'task')
  AND NOT EXISTS (
    SELECT 1 FROM links l
    WHERE l.source_id = i.id OR l.target_id = i.id
  )
GROUP BY type
ORDER BY orphaned_count DESC;

-- 15. Full project statistics
SELECT
  'Total Items' as metric,
  COUNT(*)::text as value
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'

UNION ALL

SELECT
  'Product Layer Items',
  COUNT(*)::text
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type IN ('initiative', 'epic', 'capability', 'feature', 'user_story', 'use_case', 'acceptance_criteria')

UNION ALL

SELECT
  'Total Links',
  COUNT(*)::text
FROM links l
JOIN items i ON l.source_id = i.id
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'

UNION ALL

SELECT
  'Unique Link Types',
  COUNT(DISTINCT link_type)::text
FROM links l
JOIN items i ON l.source_id = i.id
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e';
