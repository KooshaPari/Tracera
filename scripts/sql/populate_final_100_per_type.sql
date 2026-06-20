-- Final script: Create 5 projects with exactly 100+ of each type
-- Disables triggers to avoid errors, then creates all items directly
-- Only truncates if projects already exist (safe for re-runs)

-- Disable problematic triggers
ALTER TABLE projects DISABLE TRIGGER ALL;

-- Clean slate (only if tables exist and have data)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF EXISTS (SELECT 1 FROM projects LIMIT 1) THEN
            TRUNCATE TABLE projects CASCADE;
        END IF;
    END IF;
END $$;

-- Function to create complete project with exact counts
CREATE OR REPLACE FUNCTION create_project_with_exact_counts(
    p_name TEXT,
    p_slug TEXT,
    p_description TEXT,
    p_domain TEXT
) RETURNS uuid AS $$
DECLARE
    v_project_id VARCHAR(255) := gen_random_uuid()::text;
    v_req_id uuid;
    v_feat_id uuid;
    i INTEGER;
    j INTEGER;
    v_feat_num INTEGER;
BEGIN
    -- Create project (projects table doesn't have slug or status columns)
    INSERT INTO projects (id, name, project_metadata, created_at, updated_at)
    VALUES (
        v_project_id,
        p_name,
        jsonb_build_object('slug', p_slug, 'domain', p_domain, 'description', p_description, 'priority', 'high', 'status', 'active'),
        NOW(),
        NOW()
    );

    -- Create exactly 10 requirements
    FOR i IN 1..10 LOOP
        INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, created_at, updated_at, item_metadata)
        VALUES (
            gen_random_uuid(),
            v_project_id,
                'REQ-' || LPAD(i::text, 2, '0') || ': Requirement ' || i::text,
                'High-level requirement ' || i::text || ' for ' || p_name,
            'REQUIREMENT',
            'requirement',
            CASE WHEN i <= 3 THEN 'done' WHEN i <= 7 THEN 'in_progress' ELSE 'todo' END,
            CASE WHEN i <= 2 THEN 'high' WHEN i <= 5 THEN 'medium' ELSE 'low' END,
            NOW(),
            NOW(),
            jsonb_build_object('level', 'epic', 'index', i)
        )
        RETURNING id INTO v_req_id;
        
        -- Create 10 features per requirement (100 total)
        FOR j IN 1..10 LOOP
            v_feat_num := (i - 1) * 10 + j;
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'FEAT-' || LPAD(v_feat_num::text, 3, '0') || ': Feature ' || j::text || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Feature ' || j::text || ' for requirement ' || i::text,
                'FEATURE',
                'feature',
                CASE WHEN j <= 3 THEN 'done' WHEN j <= 7 THEN 'in_progress' ELSE 'todo' END,
                CASE WHEN j <= 2 THEN 'high' WHEN j <= 5 THEN 'medium' ELSE 'low' END,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i, 'feature_index', j)
            )
            RETURNING id INTO v_feat_id;
            
            -- Create 2 tests per feature (200 total)
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES
                (gen_random_uuid(), v_project_id, 'TEST-' || LPAD(((v_feat_num - 1) * 2 + 1)::text, 3, '0') || ': Unit test', 'Unit test for feature ' || v_feat_num::text, 'TEST', 'test', 'done', 'high', v_feat_id, NOW(), NOW(), jsonb_build_object('test_type', 'unit')),
                (gen_random_uuid(), v_project_id, 'TEST-' || LPAD(((v_feat_num - 1) * 2 + 2)::text, 3, '0') || ': Integration test', 'Integration test for feature ' || v_feat_num::text, 'TEST', 'test', 'todo', 'high', v_feat_id, NOW(), NOW(), jsonb_build_object('test_type', 'integration'));
            
            -- Create 1 API per feature (100 total)
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'API-' || LPAD(v_feat_num::text, 3, '0') || ': REST API',
                'REST API for feature ' || v_feat_num::text,
                'API',
                'api',
                CASE WHEN v_feat_num <= 30 THEN 'done' ELSE 'todo' END,
                'medium',
                v_feat_id,
                NOW(),
                NOW(),
                jsonb_build_object('method', 'POST', 'path', '/api/v1/features/' || v_feat_num::text)
            );
        END LOOP;
        
        -- Create 10 databases per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DB-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Database ' || j::text,
                'Database schema ' || j::text || ' for requirement ' || i::text,
                'DATABASE',
                'database',
                CASE WHEN j <= 3 THEN 'done' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('schema_name', 'req_' || i::text || '_schema_' || j::text)
            );
        END LOOP;
        
        -- Create 10 components per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'COMP-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Component ' || j::text,
                'UI component ' || j || ' for requirement ' || i,
                'COMPONENT',
                'component',
                CASE WHEN j <= 4 THEN 'done' ELSE 'todo' END,
                'low',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j % 3 WHEN 0 THEN 'form' WHEN 1 THEN 'display' ELSE 'interactive' END)
            );
        END LOOP;
        
        -- Create 10 documentation per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DOC-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Documentation ' || j::text,
                'Documentation ' || j || ' for requirement ' || i,
                'DOCUMENTATION',
                'documentation',
                CASE WHEN j <= 5 THEN 'done' ELSE 'todo' END,
                'low',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END)
            );
        END LOOP;
        
        -- Create 10 security per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'SEC-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Security ' || j::text,
                'Security review ' || j || ' for requirement ' || i,
                'SECURITY',
                'security',
                CASE WHEN j <= 3 THEN 'done' ELSE 'todo' END,
                'high',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('security_level', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END)
            );
        END LOOP;
        
        -- Create 10 performance per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'PERF-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Performance ' || j::text,
                'Performance optimization ' || j || ' for requirement ' || i,
                'PERFORMANCE',
                'performance',
                CASE WHEN j <= 4 THEN 'done' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', (j * 10)::text || 'ms')
            );
        END LOOP;
        
        -- Create 10 deployment per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DEPLOY-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': Deployment ' || j::text,
                'Deployment configuration ' || j || ' for requirement ' || i,
                'DEPLOYMENT',
                'deployment',
                CASE WHEN j <= 5 THEN 'done' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END)
            );
        END LOOP;
    END LOOP;

    -- Create comprehensive links (links table uses source_item_id, target_item_id, project_id, link_metadata)
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, feat.id, 'implements', NOW(), '{}'::jsonb
    FROM items req JOIN items feat ON feat.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND feat.project_id = v_project_id AND feat.item_type = 'feature';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, feat.id, test.id, 'tested_by', NOW(), '{}'::jsonb
    FROM items feat JOIN items test ON test.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.item_type = 'feature' AND test.project_id = v_project_id AND test.item_type = 'test';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, feat.id, api.id, 'exposes', NOW(), '{}'::jsonb
    FROM items feat JOIN items api ON api.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.item_type = 'feature' AND api.project_id = v_project_id AND api.item_type = 'api';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, db.id, 'requires', NOW(), '{}'::jsonb
    FROM items req JOIN items db ON db.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND db.project_id = v_project_id AND db.item_type = 'database';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, comp.id, 'uses', NOW(), '{}'::jsonb
    FROM items req JOIN items comp ON comp.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND comp.project_id = v_project_id AND comp.item_type = 'component';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, doc.id, 'documented_by', NOW(), '{}'::jsonb
    FROM items req JOIN items doc ON doc.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND doc.project_id = v_project_id AND doc.item_type = 'documentation';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, sec.id, 'secured_by', NOW(), '{}'::jsonb
    FROM items req JOIN items sec ON sec.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND sec.project_id = v_project_id AND sec.item_type = 'security';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, perf.id, 'optimized_by', NOW(), '{}'::jsonb
    FROM items req JOIN items perf ON perf.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND perf.project_id = v_project_id AND perf.item_type = 'performance';

    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, deploy.id, 'deployed_by', NOW(), '{}'::jsonb
    FROM items req JOIN items deploy ON deploy.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND deploy.project_id = v_project_id AND deploy.item_type = 'deployment';

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;

-- Create 5 projects
SELECT create_project_with_exact_counts('E-Commerce Platform', 'e-commerce-platform-1', 'Full-featured online shopping platform with payment integration, inventory management, and order processing', 'fullstack');
SELECT create_project_with_exact_counts('Healthcare Management System', 'healthcare-management-1', 'HIPAA-compliant patient records, appointment scheduling, and medical billing system', 'backend');
SELECT create_project_with_exact_counts('Real-Time Analytics Dashboard', 'analytics-dashboard-1', 'Data visualization platform with real-time streaming, ML predictions, and interactive charts', 'data');
SELECT create_project_with_exact_counts('Mobile Banking App', 'mobile-banking-1', 'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking', 'mobile');
SELECT create_project_with_exact_counts('DevOps Automation Platform', 'devops-automation-1', 'CI/CD pipeline automation, infrastructure as code, monitoring, and deployment orchestration', 'devops');

-- Re-enable triggers
ALTER TABLE projects ENABLE TRIGGER ALL;

-- Summary query - verify exact counts
SELECT 
    p.name,
    COUNT(DISTINCT i.id) as total_items,
    COUNT(DISTINCT CASE WHEN i.item_type = 'requirement' THEN i.id END) as requirements,
    COUNT(DISTINCT CASE WHEN i.item_type = 'feature' THEN i.id END) as features,
    COUNT(DISTINCT CASE WHEN i.item_type = 'test' THEN i.id END) as tests,
    COUNT(DISTINCT CASE WHEN i.item_type = 'api' THEN i.id END) as apis,
    COUNT(DISTINCT CASE WHEN i.item_type = 'database' THEN i.id END) as databases,
    COUNT(DISTINCT CASE WHEN i.item_type = 'component' THEN i.id END) as components,
    COUNT(DISTINCT CASE WHEN i.item_type = 'documentation' THEN i.id END) as documentation,
    COUNT(DISTINCT CASE WHEN i.item_type = 'security' THEN i.id END) as security,
    COUNT(DISTINCT CASE WHEN i.item_type = 'performance' THEN i.id END) as performance,
    COUNT(DISTINCT CASE WHEN i.item_type = 'deployment' THEN i.id END) as deployment,
    COUNT(DISTINCT l.id) as total_links
FROM projects p
LEFT JOIN items i ON i.project_id = p.id AND i.deleted_at IS NULL
LEFT JOIN links l ON (l.source_item_id = i.id OR l.target_item_id = i.id)
WHERE p.name IN ('E-Commerce Platform', 'Healthcare Management System', 'Real-Time Analytics Dashboard', 'Mobile Banking App', 'DevOps Automation Platform')
GROUP BY p.id, p.name
ORDER BY p.name;
