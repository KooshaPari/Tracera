-- Final script: Create 5 projects with exactly 100+ of each type
-- Disables triggers to avoid errors, then creates all items directly

-- Disable problematic triggers
ALTER TABLE projects DISABLE TRIGGER ALL;

-- Clean slate
TRUNCATE TABLE projects CASCADE;

-- Function to create complete project with exact counts
CREATE OR REPLACE FUNCTION create_project_with_exact_counts(
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
    v_feat_num INTEGER;
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

    -- Create exactly 10 requirements
    FOR i IN 1..10 LOOP
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
        
        -- Create 10 features per requirement (100 total)
        FOR j IN 1..10 LOOP
            v_feat_num := (i - 1) * 10 + j;
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'FEAT-' || LPAD(v_feat_num::text, 3, '0') || ': Feature ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Feature ' || j || ' for requirement ' || i,
                'feature',
                CASE WHEN j <= 3 THEN 'closed' WHEN j <= 7 THEN 'in_progress' ELSE 'open' END,
                CASE WHEN j <= 2 THEN 2 WHEN j <= 5 THEN 1 ELSE 0 END,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i, 'feature_index', j)
            )
            RETURNING id INTO v_feat_id;
            
            -- Create 2 tests per feature (200 total)
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES
                (gen_random_uuid(), v_project_id, 'TEST-' || LPAD((v_feat_num - 1) * 2 + 1::text, 3, '0') || ': Unit test', 'Unit test for feature ' || v_feat_num, 'test', 'closed', 1, v_feat_id, NOW(), NOW(), jsonb_build_object('test_type', 'unit')),
                (gen_random_uuid(), v_project_id, 'TEST-' || LPAD((v_feat_num - 1) * 2 + 2::text, 3, '0') || ': Integration test', 'Integration test for feature ' || v_feat_num, 'test', 'open', 1, v_feat_id, NOW(), NOW(), jsonb_build_object('test_type', 'integration'));
            
            -- Create 1 API per feature (100 total)
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'API-' || LPAD(v_feat_num::text, 3, '0') || ': REST API',
                'REST API for feature ' || v_feat_num,
                'api',
                CASE WHEN v_feat_num <= 30 THEN 'closed' ELSE 'open' END,
                2,
                v_feat_id,
                NOW(),
                NOW(),
                jsonb_build_object('method', 'POST', 'path', '/api/v1/features/' || v_feat_num)
            );
        END LOOP;
        
        -- Create 10 databases per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DB-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Database ' || j,
                'Database schema ' || j || ' for requirement ' || i,
                'database',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('schema_name', 'req_' || i || '_schema_' || j)
            );
        END LOOP;
        
        -- Create 10 components per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'COMP-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Component ' || j,
                'UI component ' || j || ' for requirement ' || i,
                'component',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                1,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j % 3 WHEN 0 THEN 'form' WHEN 1 THEN 'display' ELSE 'interactive' END)
            );
        END LOOP;
        
        -- Create 10 documentation per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DOC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Documentation ' || j,
                'Documentation ' || j || ' for requirement ' || i,
                'documentation',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                1,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END)
            );
        END LOOP;
        
        -- Create 10 security per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'SEC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Security ' || j,
                'Security review ' || j || ' for requirement ' || i,
                'security',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                3,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('security_level', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END)
            );
        END LOOP;
        
        -- Create 10 performance per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'PERF-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Performance ' || j,
                'Performance optimization ' || j || ' for requirement ' || i,
                'performance',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', (j * 10) || 'ms')
            );
        END LOOP;
        
        -- Create 10 deployment per requirement (100 total)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DEPLOY-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Deployment ' || j,
                'Deployment configuration ' || j || ' for requirement ' || i,
                'deployment',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                2,
                v_req_id,
                NOW(),
                NOW(),
                jsonb_build_object('environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END)
            );
        END LOOP;
    END LOOP;

    -- Create comprehensive links
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, feat.id, 'implements', NOW(), '{}'::jsonb
    FROM items req JOIN items feat ON feat.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND feat.project_id = v_project_id AND feat.type = 'feature';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, test.id, 'tested_by', NOW(), '{}'::jsonb
    FROM items feat JOIN items test ON test.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature' AND test.project_id = v_project_id AND test.type = 'test';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, api.id, 'exposes', NOW(), '{}'::jsonb
    FROM items feat JOIN items api ON api.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature' AND api.project_id = v_project_id AND api.type = 'api';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, db.id, 'requires', NOW(), '{}'::jsonb
    FROM items req JOIN items db ON db.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND db.project_id = v_project_id AND db.type = 'database';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, comp.id, 'uses', NOW(), '{}'::jsonb
    FROM items req JOIN items comp ON comp.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND comp.project_id = v_project_id AND comp.type = 'component';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, doc.id, 'documented_by', NOW(), '{}'::jsonb
    FROM items req JOIN items doc ON doc.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND doc.project_id = v_project_id AND doc.type = 'documentation';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, sec.id, 'secured_by', NOW(), '{}'::jsonb
    FROM items req JOIN items sec ON sec.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND sec.project_id = v_project_id AND sec.type = 'security';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, perf.id, 'optimized_by', NOW(), '{}'::jsonb
    FROM items req JOIN items perf ON perf.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND perf.project_id = v_project_id AND perf.type = 'performance';

    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, deploy.id, 'deployed_by', NOW(), '{}'::jsonb
    FROM items req JOIN items deploy ON deploy.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement' AND deploy.project_id = v_project_id AND deploy.type = 'deployment';

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

-- Summary
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
WHERE p.deleted_at IS NULL AND p.name IN ('E-Commerce Platform', 'Healthcare Management System', 'Real-Time Analytics Dashboard', 'Mobile Banking App', 'DevOps Automation Platform')
GROUP BY p.id, p.name
ORDER BY p.name;
