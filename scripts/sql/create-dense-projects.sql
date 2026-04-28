-- Script to create 5 dense, complete projects with comprehensive data
-- Run with: psql -d your_database -f scripts/create-dense-projects.sql
-- Or: sqlite3 your_database.db < scripts/create-dense-projects.sql

-- Project 1: E-Commerce Platform
INSERT INTO projects (id, name, description, project_metadata, created_at, updated_at)
VALUES (
    'proj-ecommerce-' || substr(md5(random()::text), 1, 8),
    'E-Commerce Platform',
    'Full-featured online shopping platform with payment integration, inventory management, and order processing',
    '{"domain": "fullstack", "priority": "high"}'::jsonb,
    NOW(),
    NOW()
) RETURNING id INTO project1_id;

-- Project 2: Healthcare Management System
INSERT INTO projects (id, name, description, project_metadata, created_at, updated_at)
VALUES (
    'proj-healthcare-' || substr(md5(random()::text), 1, 8),
    'Healthcare Management System',
    'HIPAA-compliant patient records, appointment scheduling, and medical billing system',
    '{"domain": "backend", "priority": "critical"}'::jsonb,
    NOW(),
    NOW()
) RETURNING id INTO project2_id;

-- Project 3: Real-Time Analytics Dashboard
INSERT INTO projects (id, name, description, project_metadata, created_at, updated_at)
VALUES (
    'proj-analytics-' || substr(md5(random()::text), 1, 8),
    'Real-Time Analytics Dashboard',
    'Data visualization platform with real-time streaming, ML predictions, and interactive charts',
    '{"domain": "data", "priority": "high"}'::jsonb,
    NOW(),
    NOW()
) RETURNING id INTO project3_id;

-- Project 4: Mobile Banking App
INSERT INTO projects (id, name, description, project_metadata, created_at, updated_at)
VALUES (
    'proj-banking-' || substr(md5(random()::text), 1, 8),
    'Mobile Banking App',
    'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking',
    '{"domain": "mobile", "priority": "critical"}'::jsonb,
    NOW(),
    NOW()
) RETURNING id INTO project4_id;

-- Project 5: DevOps Automation Platform
INSERT INTO projects (id, name, description, project_metadata, created_at, updated_at)
VALUES (
    'proj-devops-' || substr(md5(random()::text), 1, 8),
    'DevOps Automation Platform',
    'CI/CD pipeline automation, infrastructure as code, monitoring, and deployment orchestration',
    '{"domain": "devops", "priority": "high"}'::jsonb,
    NOW(),
    NOW()
) RETURNING id INTO project5_id;

-- Helper function to create items for a project
CREATE OR REPLACE FUNCTION create_dense_project_items(
    p_project_id TEXT,
    p_item_count INTEGER DEFAULT 500
) RETURNS VOID AS $$
DECLARE
    i INTEGER;
    item_types TEXT[] := ARRAY['requirement', 'feature', 'code', 'test', 'api', 'database', 'wireframe', 'documentation', 'deployment'];
    statuses TEXT[] := ARRAY['pending', 'in_progress', 'completed', 'blocked'];
    priorities TEXT[] := ARRAY['low', 'medium', 'high', 'critical'];
    item_type TEXT;
    item_status TEXT;
    item_priority TEXT;
    item_id TEXT;
BEGIN
    FOR i IN 1..p_item_count LOOP
        item_type := item_types[1 + floor(random() * array_length(item_types, 1))::int];
        item_status := statuses[1 + floor(random() * array_length(statuses, 1))::int];
        item_priority := priorities[1 + floor(random() * array_length(priorities, 1))::int];
        item_id := 'item-' || substr(md5(random()::text || i::text), 1, 16);
        
        INSERT INTO items (
            id, project_id, title, description, view, item_type, status, priority,
            created_at, updated_at
        ) VALUES (
            item_id,
            p_project_id,
            CASE item_type
                WHEN 'requirement' THEN 'REQ-' || i || ': ' || array['User authentication', 'Payment processing', 'Data encryption', 'API rate limiting', 'Real-time notifications'][1 + floor(random() * 5)::int]
                WHEN 'feature' THEN 'Feature ' || i || ': ' || array['User dashboard', 'Search functionality', 'Export reports', 'Bulk operations', 'Dark mode'][1 + floor(random() * 5)::int]
                WHEN 'code' THEN 'src/modules/module_' || i || '.ts'
                WHEN 'test' THEN 'Test ' || i || ': ' || array['Unit test', 'Integration test', 'E2E test', 'Performance test', 'Security test'][1 + floor(random() * 5)::int]
                WHEN 'api' THEN 'API ' || i || ': ' || array['GET /api/v1/users', 'POST /api/v1/orders', 'PUT /api/v1/products', 'DELETE /api/v1/cart', 'PATCH /api/v1/profile'][1 + floor(random() * 5)::int]
                WHEN 'database' THEN 'DB Schema ' || i || ': ' || array['users table', 'orders table', 'products table', 'payments table', 'inventory table'][1 + floor(random() * 5)::int]
                WHEN 'wireframe' THEN 'Wireframe ' || i || ': ' || array['Login screen', 'Dashboard', 'Product page', 'Checkout flow', 'Settings page'][1 + floor(random() * 5)::int]
                WHEN 'documentation' THEN 'Doc ' || i || ': ' || array['API documentation', 'User guide', 'Architecture diagram', 'Deployment guide', 'Troubleshooting'][1 + floor(random() * 5)::int]
                ELSE 'Deploy ' || i || ': ' || array['Production', 'Staging', 'Development', 'CI/CD pipeline', 'Monitoring'][1 + floor(random() * 5)::int]
            END,
            'Comprehensive ' || item_type || ' implementation for project requirements. Includes detailed specifications, implementation notes, and testing considerations.',
            item_type,
            item_type,
            item_status,
            item_priority,
            NOW() - (random() * interval '30 days'),
            NOW() - (random() * interval '7 days')
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create items for each project
SELECT create_dense_project_items((SELECT id FROM projects WHERE name = 'E-Commerce Platform' LIMIT 1), 500);
SELECT create_dense_project_items((SELECT id FROM projects WHERE name = 'Healthcare Management System' LIMIT 1), 500);
SELECT create_dense_project_items((SELECT id FROM projects WHERE name = 'Real-Time Analytics Dashboard' LIMIT 1), 500);
SELECT create_dense_project_items((SELECT id FROM projects WHERE name = 'Mobile Banking App' LIMIT 1), 500);
SELECT create_dense_project_items((SELECT id FROM projects WHERE name = 'DevOps Automation Platform' LIMIT 1), 500);

-- Create traceability links between items
CREATE OR REPLACE FUNCTION create_dense_project_links(
    p_project_id TEXT,
    p_link_count INTEGER DEFAULT 300
) RETURNS VOID AS $$
DECLARE
    i INTEGER;
    link_types TEXT[] := ARRAY['implements', 'tests', 'depends_on', 'relates_to', 'validates', 'blocks'];
    source_item RECORD;
    target_item RECORD;
    link_type TEXT;
    link_id TEXT;
BEGIN
    FOR i IN 1..p_link_count LOOP
        -- Get random source and target items from the project
        SELECT * INTO source_item FROM items WHERE project_id = p_project_id ORDER BY random() LIMIT 1;
        SELECT * INTO target_item FROM items WHERE project_id = p_project_id AND id != source_item.id ORDER BY random() LIMIT 1;
        
        link_type := link_types[1 + floor(random() * array_length(link_types, 1))::int];
        link_id := 'link-' || substr(md5(random()::text || i::text), 1, 16);
        
        INSERT INTO links (
            id, project_id, source_item_id, target_item_id, link_type, link_metadata,
            created_at, updated_at
        ) VALUES (
            link_id,
            p_project_id,
            source_item.id,
            target_item.id,
            link_type,
            '{}'::jsonb,
            NOW() - (random() * interval '20 days'),
            NOW() - (random() * interval '5 days')
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create links for each project
SELECT create_dense_project_links((SELECT id FROM projects WHERE name = 'E-Commerce Platform' LIMIT 1), 300);
SELECT create_dense_project_links((SELECT id FROM projects WHERE name = 'Healthcare Management System' LIMIT 1), 300);
SELECT create_dense_project_links((SELECT id FROM projects WHERE name = 'Real-Time Analytics Dashboard' LIMIT 1), 300);
SELECT create_dense_project_links((SELECT id FROM projects WHERE name = 'Mobile Banking App' LIMIT 1), 300);
SELECT create_dense_project_links((SELECT id FROM projects WHERE name = 'DevOps Automation Platform' LIMIT 1), 300);

-- Cleanup functions
DROP FUNCTION IF EXISTS create_dense_project_items(TEXT, INTEGER);
DROP FUNCTION IF EXISTS create_dense_project_links(TEXT, INTEGER);

-- Summary
SELECT 
    p.name as project_name,
    COUNT(DISTINCT i.id) as item_count,
    COUNT(DISTINCT l.id) as link_count,
    COUNT(DISTINCT CASE WHEN i.status = 'completed' THEN i.id END) as completed_items
FROM projects p
LEFT JOIN items i ON i.project_id = p.id
LEFT JOIN links l ON l.project_id = p.id
WHERE p.name IN (
    'E-Commerce Platform',
    'Healthcare Management System',
    'Real-Time Analytics Dashboard',
    'Mobile Banking App',
    'DevOps Automation Platform'
)
GROUP BY p.id, p.name
ORDER BY p.name;
