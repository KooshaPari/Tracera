-- Clean script: Create 5 projects with exactly 100+ of each type
-- This script ensures exact counts by creating items directly in nested loops

-- Disable problematic triggers
ALTER TABLE projects DISABLE TRIGGER ALL;

-- Clean slate - delete all projects
TRUNCATE TABLE projects CASCADE;

-- Function to create one complete project with exact counts
CREATE OR REPLACE FUNCTION create_project_exact_100(
    p_name TEXT,
    p_slug TEXT,
    p_description TEXT,
    p_domain TEXT
) RETURNS uuid AS $$
DECLARE
    v_project_id uuid := gen_random_uuid();
    v_req_id uuid;
    v_feat_id uuid;
    i INTEGER;
    j INTEGER;
    v_feat_counter INTEGER := 0;
BEGIN
    -- Create project
    INSERT INTO projects (id, name, slug, status, metadata, created_at, updated_at)
    VALUES (
        v_project_id,
        p_name,
        p_slug,
        'active',
        jsonb_build_object('domain', p_domain, 'description', p_description, 'priority', 'high'),
        NOW(),
        NOW()
    );

    -- Create exactly 10 requirements, and for each requirement create all child items
    FOR i IN 1..10 LOOP
        -- Create requirement
        INSERT INTO items (id, project_id, title, description, type, status, priority, created_at, updated_at, metadata)
        VALUES (
            gen_random_uuid(),
            v_project_id,
            'REQ-' || LPAD(i::text, 2, '0') || ': Requirement ' || i,
            'High-level requirement ' || i || ' for ' || p_name,
            'requirement',
            CASE WHEN i <= 3 THEN 'closed' WHEN i <= 7 THEN 'in_progress' ELSE 'open' END,
            CASE WHEN i <= 2 THEN 3 WHEN i <= 5 THEN 2 ELSE 1 END,
            NOW(),
            NOW(),
            jsonb_build_object('level', 'epic', 'index', i)
        )
        RETURNING id INTO v_req_id;
        
        -- Create exactly 10 features per requirement (100 total)
        FOR j IN 1..10 LOOP
            v_feat_counter := v_feat_counter + 1;
            
            -- Create feature
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'FEAT-' || LPAD(v_feat_counter::text, 3, '0') || ': Feature ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Feature ' || j || ' for requirement ' || i || ' in ' || p_name,
                'feature',
                CASE WHEN j <= 3 THEN 'closed' WHEN j <= 7 THEN 'in_progress' ELSE 'open' END,
                CASE WHEN j <= 2 THEN 2 WHEN j <= 5 THEN 1 ELSE 0 END,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i, 'feature_index', j, 'feature_number', v_feat_counter)
            )
            RETURNING id INTO v_feat_id;
            
            -- Create exactly 2 tests per feature (200 total)
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES
                (
                    gen_random_uuid(),
                    v_project_id,
                    'TEST-' || LPAD((v_feat_counter - 1) * 2 + 1::text, 3, '0') || ': Unit test for FEAT-' || LPAD(v_feat_counter::text, 3, '0'),
                    'Unit test for feature ' || v_feat_counter,
                    'test',
                    'closed',
                    1,
                    v_feat_id,
                    NOW(),
                    NOW(),
                    jsonb_build_object('test_type', 'unit', 'feature_number', v_feat_counter)
                ),
                (
                    gen_random_uuid(),
                    v_project_id,
                    'TEST-' || LPAD((v_feat_counter - 1) * 2 + 2::text, 3, '0') || ': Integration test for FEAT-' || LPAD(v_feat_counter::text, 3, '0'),
                    'Integration test for feature ' || v_feat_counter,
                    'test',
                    'open',
                    1,
                    v_feat_id,
                    NOW(),
                    NOW(),
                    jsonb_build_object('test_type', 'integration', 'feature_number', v_feat_counter)
                );
            
            -- Create exactly 1 API per feature (100 total)
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'API-' || LPAD(v_feat_counter::text, 3, '0') || ': REST API for FEAT-' || LPAD(v_feat_counter::text, 3, '0'),
                'REST API endpoint for feature ' || v_feat_counter,
                'api',
                CASE WHEN v_feat_counter <= 30 THEN 'closed' ELSE 'open' END,
                2,
                v_feat_id,
                NOW(),
                NOW(),
                jsonb_build_object('method', CASE WHEN v_feat_counter % 4 = 0 THEN 'GET' WHEN v_feat_counter % 4 = 1 THEN 'POST' WHEN v_feat_counter % 4 = 2 THEN 'PUT' ELSE 'DELETE' END, 'path', '/api/v1/features/' || v_feat_counter, 'feature_number', v_feat_counter)
            );
        END LOOP;
        
        -- Create exactly 10 databases per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DB-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Database ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Database schema ' || j || ' for requirement ' || i,
                'database',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('schema_name', 'req_' || i || '_schema_' || j, 'tables', j * 3, 'requirement_id', i)
            );
        END LOOP;
        
        -- Create exactly 10 components per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'COMP-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Component ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'UI component ' || j || ' for requirement ' || i,
                'component',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                1,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j % 3 WHEN 0 THEN 'form' WHEN 1 THEN 'display' ELSE 'interactive' END, 'framework', 'react', 'requirement_id', i)
            );
        END LOOP;
        
        -- Create exactly 10 documentation per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DOC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Documentation ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Documentation ' || j || ' for requirement ' || i,
                'documentation',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                1,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END, 'requirement_id', i)
            );
        END LOOP;
        
        -- Create exactly 10 security per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'SEC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Security ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Security review ' || j || ' for requirement ' || i,
                'security',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                3,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('security_level', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END, 'compliance', 'SOC2', 'requirement_id', i)
            );
        END LOOP;
        
        -- Create exactly 10 performance per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'PERF-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Performance ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Performance optimization ' || j || ' for requirement ' || i,
                'performance',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', (j * 10) || 'ms', 'throughput', (j * 100) || 'req/s', 'requirement_id', i)
            );
        END LOOP;
        
        -- Create exactly 10 deployment per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DEPLOY-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Deployment ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Deployment configuration ' || j || ' for requirement ' || i,
                'deployment',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END, 'platform', 'kubernetes', 'requirement_id', i)
            );
        END LOOP;
    END LOOP;

    -- Create comprehensive links between items
    -- Requirements -> Features
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, feat.id, 'implements', NOW(), jsonb_build_object('link_type', 'requirement_to_feature')
    FROM items req
    JOIN items feat ON feat.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND feat.project_id = v_project_id AND feat.type = 'feature';

    -- Features -> Tests
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, test.id, 'tested_by', NOW(), jsonb_build_object('link_type', 'feature_to_test')
    FROM items feat
    JOIN items test ON test.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature'
      AND test.project_id = v_project_id AND test.type = 'test';

    -- Features -> APIs
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, api.id, 'exposes', NOW(), jsonb_build_object('link_type', 'feature_to_api')
    FROM items feat
    JOIN items api ON api.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature'
      AND api.project_id = v_project_id AND api.type = 'api';

    -- Requirements -> Databases
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, db.id, 'requires', NOW(), jsonb_build_object('link_type', 'requirement_to_database')
    FROM items req
    JOIN items db ON db.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND db.project_id = v_project_id AND db.type = 'database';

    -- Requirements -> Components
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, comp.id, 'uses', NOW(), jsonb_build_object('link_type', 'requirement_to_component')
    FROM items req
    JOIN items comp ON comp.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND comp.project_id = v_project_id AND comp.type = 'component';

    -- Requirements -> Documentation
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, doc.id, 'documented_by', NOW(), jsonb_build_object('link_type', 'requirement_to_documentation')
    FROM items req
    JOIN items doc ON doc.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND doc.project_id = v_project_id AND doc.type = 'documentation';

    -- Requirements -> Security
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, sec.id, 'secured_by', NOW(), jsonb_build_object('link_type', 'requirement_to_security')
    FROM items req
    JOIN items sec ON sec.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND sec.project_id = v_project_id AND sec.type = 'security';

    -- Requirements -> Performance
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, perf.id, 'optimized_by', NOW(), jsonb_build_object('link_type', 'requirement_to_performance')
    FROM items req
    JOIN items perf ON perf.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND perf.project_id = v_project_id AND perf.type = 'performance';

    -- Requirements -> Deployment
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, deploy.id, 'deployed_by', NOW(), jsonb_build_object('link_type', 'requirement_to_deployment')
    FROM items req
    JOIN items deploy ON deploy.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND deploy.project_id = v_project_id AND deploy.type = 'deployment';

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;

-- Create 5 projects (one at a time to avoid conflicts)
SELECT create_project_exact_100('E-Commerce Platform', 'e-commerce-platform', 'Full-featured online shopping platform with payment integration, inventory management, and order processing', 'fullstack');
SELECT create_project_exact_100('Healthcare Management System', 'healthcare-management-system', 'HIPAA-compliant patient records, appointment scheduling, and medical billing system', 'backend');
SELECT create_project_exact_100('Real-Time Analytics Dashboard', 'real-time-analytics-dashboard', 'Data visualization platform with real-time streaming, ML predictions, and interactive charts', 'data');
SELECT create_project_exact_100('Mobile Banking App', 'mobile-banking-app', 'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking', 'mobile');
SELECT create_project_exact_100('DevOps Automation Platform', 'devops-automation-platform', 'CI/CD pipeline automation, infrastructure as code, monitoring, and deployment orchestration', 'devops');

-- Re-enable triggers
ALTER TABLE projects ENABLE TRIGGER ALL;

-- Summary query - verify exact counts
SELECT 
    p.name,
    COUNT(DISTINCT i.id) as total_items,
    COUNT(DISTINCT CASE WHEN i.type = 'requirement' THEN i.id END) as requirements,
    COUNT(DISTINCT CASE WHEN i.type = 'feature' THEN i.id END) as features,
    COUNT(DISTINCT CASE WHEN i.type = 'test' THEN i.id END) as tests,
    COUNT(DISTINCT CASE WHEN i.type = 'api' THEN i.id END) as apis,
    COUNT(DISTINCT CASE WHEN i.type = 'database' THEN i.id END) as databases,
    COUNT(DISTINCT CASE WHEN i.type = 'component' THEN i.id END) as components,
    COUNT(DISTINCT CASE WHEN i.type = 'documentation' THEN i.id END) as documentation,
    COUNT(DISTINCT CASE WHEN i.type = 'security' THEN i.id END) as security,
    COUNT(DISTINCT CASE WHEN i.type = 'performance' THEN i.id END) as performance,
    COUNT(DISTINCT CASE WHEN i.type = 'deployment' THEN i.id END) as deployment,
    COUNT(DISTINCT l.id) as total_links
FROM projects p
LEFT JOIN items i ON i.project_id = p.id AND i.deleted_at IS NULL
LEFT JOIN links l ON (l.source_id = i.id OR l.target_id = i.id)
WHERE p.deleted_at IS NULL 
  AND p.name IN ('E-Commerce Platform', 'Healthcare Management System', 'Real-Time Analytics Dashboard', 'Mobile Banking App', 'DevOps Automation Platform')
GROUP BY p.id, p.name
ORDER BY p.name;
