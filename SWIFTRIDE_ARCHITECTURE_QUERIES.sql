-- SwiftRide Architecture - Sample Queries
-- Database: tracertm
-- Project ID: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e

-- ========================================
-- SUMMARY QUERIES
-- ========================================

-- Overall architecture summary
SELECT
  type,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY type
ORDER BY count DESC;

-- Total count
SELECT COUNT(*) as total_architecture_items
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e';

-- ========================================
-- MICROSERVICES QUERIES
-- ========================================

-- All microservices by category
SELECT
  metadata->>'category' as category,
  title,
  description,
  metadata->>'language' as language
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'microservice'
ORDER BY category, title;

-- Core microservices
SELECT title, description, metadata->>'service_code' as code
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'microservice'
  AND metadata->>'category' = 'core'
ORDER BY title;

-- Integration services
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'microservice'
  AND metadata->>'category' = 'integration'
ORDER BY title;

-- Services by programming language
SELECT
  metadata->>'language' as language,
  COUNT(*) as service_count,
  array_agg(title ORDER BY title) as services
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'microservice'
GROUP BY metadata->>'language'
ORDER BY service_count DESC;

-- ========================================
-- API ENDPOINT QUERIES
-- ========================================

-- All API endpoints by method
SELECT
  metadata->>'method' as method,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
GROUP BY metadata->>'method'
ORDER BY count DESC;

-- Endpoints by access level
SELECT
  metadata->>'access_level' as access_level,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
GROUP BY metadata->>'access_level'
ORDER BY count DESC;

-- Driver API endpoints
SELECT
  metadata->>'method' as method,
  metadata->>'path' as path,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
  AND metadata->>'path' LIKE '%/drivers/%'
ORDER BY path;

-- Rider API endpoints
SELECT
  metadata->>'method' as method,
  metadata->>'path' as path,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
  AND metadata->>'path' LIKE '%/riders/%'
ORDER BY path;

-- WebSocket endpoints
SELECT
  metadata->>'path' as websocket_path,
  description,
  metadata->>'access_level' as access
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
  AND metadata->>'method' = 'WS'
ORDER BY websocket_path;

-- Admin endpoints
SELECT
  metadata->>'method' as method,
  metadata->>'path' as path,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint'
  AND metadata->>'access_level' = 'admin'
ORDER BY path;

-- ========================================
-- DATA MODEL QUERIES
-- ========================================

-- Data models by type
SELECT
  metadata->>'model_type' as model_type,
  COUNT(*) as count,
  array_agg(title ORDER BY title) as models
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'data_model'
GROUP BY metadata->>'model_type'
ORDER BY count DESC;

-- Aggregate roots
SELECT
  title,
  description,
  metadata->'fields' as fields
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'data_model'
  AND metadata->>'model_type' = 'aggregate'
ORDER BY title;

-- Entities
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'data_model'
  AND metadata->>'model_type' = 'entity'
ORDER BY title;

-- Value objects
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'data_model'
  AND metadata->>'model_type' = 'value_object'
ORDER BY title;

-- ========================================
-- DATABASE TABLE QUERIES
-- ========================================

-- All database tables
SELECT
  title as table_name,
  description,
  metadata->'columns' as columns
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
ORDER BY title;

-- Tables with timestamps
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
  AND (metadata->>'has_timestamps')::boolean = true
ORDER BY title;

-- Driver-related tables
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
  AND title LIKE 'driver%'
ORDER BY title;

-- Rider-related tables
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
  AND title LIKE 'rider%'
ORDER BY title;

-- Trip-related tables
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
  AND title LIKE 'trip%'
ORDER BY title;

-- Payment-related tables
SELECT title, description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_table'
  AND title LIKE 'payment%'
ORDER BY title;

-- ========================================
-- DATABASE INDEX QUERIES
-- ========================================

-- Indexes by type
SELECT
  metadata->>'index_type' as index_type,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_index'
GROUP BY metadata->>'index_type'
ORDER BY count DESC;

-- Unique indexes
SELECT
  title as index_name,
  metadata->>'table' as table_name,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_index'
  AND (metadata->>'unique')::boolean = true
ORDER BY table_name, index_name;

-- Geospatial indexes (GiST)
SELECT
  title as index_name,
  metadata->>'table' as table_name,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_index'
  AND metadata->>'index_type' LIKE '%gist%'
ORDER BY table_name;

-- Full-text search indexes (GIN)
SELECT
  title as index_name,
  metadata->>'table' as table_name,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_index'
  AND metadata->>'index_type' = 'gin'
ORDER BY table_name;

-- Time-series indexes (BRIN)
SELECT
  title as index_name,
  metadata->>'table' as table_name,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'database_index'
  AND metadata->>'index_type' = 'brin'
ORDER BY table_name;

-- ========================================
-- INTEGRATION POINT QUERIES
-- ========================================

-- Integrations by provider
SELECT
  metadata->>'provider' as provider,
  COUNT(*) as integration_count,
  array_agg(title ORDER BY title) as integrations
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'integration_point'
GROUP BY metadata->>'provider'
ORDER BY integration_count DESC;

-- Integrations by category
SELECT
  metadata->>'category' as category,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'integration_point'
GROUP BY metadata->>'category'
ORDER BY count DESC;

-- Payment integrations
SELECT
  title,
  description,
  metadata->>'provider' as provider,
  metadata->>'endpoint' as endpoint
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'integration_point'
  AND metadata->>'category' = 'payment'
ORDER BY provider, title;

-- Communication integrations
SELECT
  title,
  description,
  metadata->>'provider' as provider
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'integration_point'
  AND metadata->>'category' = 'communication'
ORDER BY provider;

-- Location/mapping integrations
SELECT
  title,
  description,
  metadata->>'provider' as provider
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'integration_point'
  AND metadata->>'category' = 'location'
ORDER BY provider;

-- ========================================
-- DOMAIN EVENT QUERIES
-- ========================================

-- Events by domain
SELECT
  metadata->>'domain' as domain,
  COUNT(*) as event_count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
GROUP BY metadata->>'domain'
ORDER BY event_count DESC;

-- Events by category
SELECT
  metadata->>'domain' as domain,
  metadata->>'category' as category,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
GROUP BY metadata->>'domain', metadata->>'category'
ORDER BY domain, category;

-- Driver events
SELECT
  title as event_name,
  description,
  metadata->>'category' as category
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
  AND metadata->>'domain' = 'driver'
ORDER BY category, title;

-- Rider events
SELECT
  title as event_name,
  description,
  metadata->>'category' as category
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
  AND metadata->>'domain' = 'rider'
ORDER BY category, title;

-- Trip events
SELECT
  title as event_name,
  description,
  metadata->>'category' as category
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
  AND metadata->>'domain' = 'trip'
ORDER BY category, title;

-- Payment events
SELECT
  title as event_name,
  description,
  metadata->>'category' as category
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
  AND metadata->>'domain' = 'payment'
ORDER BY category, title;

-- System events
SELECT
  title as event_name,
  description,
  metadata->>'category' as category
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'event'
  AND metadata->>'domain' = 'system'
ORDER BY category, title;

-- ========================================
-- MESSAGE QUEUE QUERIES
-- ========================================

-- Queues by domain
SELECT
  metadata->>'domain' as domain,
  COUNT(*) as queue_count,
  array_agg(metadata->>'subject' ORDER BY title) as subjects
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'message_queue'
GROUP BY metadata->>'domain'
ORDER BY queue_count DESC;

-- All NATS subjects
SELECT
  metadata->>'subject' as nats_subject,
  description,
  metadata->>'domain' as domain
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'message_queue'
ORDER BY nats_subject;

-- Driver queues
SELECT
  metadata->>'subject' as subject,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'message_queue'
  AND metadata->>'domain' = 'driver'
ORDER BY subject;

-- Trip queues
SELECT
  metadata->>'subject' as subject,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'message_queue'
  AND metadata->>'domain' = 'trip'
ORDER BY subject;

-- ========================================
-- CROSS-CUTTING QUERIES
-- ========================================

-- Complete architecture breakdown
SELECT
  'Microservices' as component,
  COUNT(*) as total,
  COUNT(CASE WHEN metadata->>'category' = 'core' THEN 1 END) as core,
  COUNT(CASE WHEN metadata->>'category' = 'driver' THEN 1 END) as driver_domain,
  COUNT(CASE WHEN metadata->>'category' = 'rider' THEN 1 END) as rider_domain,
  COUNT(CASE WHEN metadata->>'category' = 'integration' THEN 1 END) as integrations,
  COUNT(CASE WHEN metadata->>'category' = 'operations' THEN 1 END) as operations
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'microservice'

UNION ALL

SELECT
  'API Endpoints' as component,
  COUNT(*) as total,
  COUNT(CASE WHEN metadata->>'path' LIKE '%/drivers/%' THEN 1 END) as driver_apis,
  COUNT(CASE WHEN metadata->>'path' LIKE '%/riders/%' THEN 1 END) as rider_apis,
  COUNT(CASE WHEN metadata->>'path' LIKE '%/trips/%' THEN 1 END) as trip_apis,
  COUNT(CASE WHEN metadata->>'access_level' = 'admin' THEN 1 END) as admin_apis,
  COUNT(CASE WHEN metadata->>'method' = 'WS' THEN 1 END) as websockets
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'api_endpoint';

-- Search for specific keywords
SELECT
  type,
  title,
  description
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND (
    title ILIKE '%real-time%'
    OR description ILIKE '%real-time%'
  )
ORDER BY type, title;

-- Architecture coverage by domain
SELECT
  CASE
    WHEN title LIKE '%river%' OR description LIKE '%river%' THEN 'Driver'
    WHEN title LIKE '%ider%' OR description LIKE '%ider%' THEN 'Rider'
    WHEN title LIKE '%rip%' OR description LIKE '%rip%' THEN 'Trip'
    WHEN title LIKE '%ayment%' OR description LIKE '%ayment%' THEN 'Payment'
    ELSE 'Other'
  END as domain,
  type,
  COUNT(*) as count
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY domain, type
ORDER BY domain, type;

-- ========================================
-- EXPORT QUERIES
-- ========================================

-- Export complete architecture as JSON
SELECT json_agg(
  json_build_object(
    'id', id,
    'type', type,
    'title', title,
    'description', description,
    'metadata', metadata,
    'created_at', created_at
  ) ORDER BY type, title
) as architecture_json
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e';

-- Export by type
SELECT type, json_agg(
  json_build_object(
    'title', title,
    'description', description,
    'metadata', metadata
  ) ORDER BY title
) as items_json
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY type;
