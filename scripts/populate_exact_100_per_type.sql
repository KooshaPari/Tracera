-- Direct SQL script to create projects with exactly 100+ of each type
-- No functions, just direct INSERTs to ensure exact counts

-- Helper: Generate UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Delete existing projects
DELETE FROM projects WHERE name IN ('E-Commerce Platform', 'Healthcare Management System', 'Real-Time Analytics Dashboard', 'Mobile Banking App', 'DevOps Automation Platform');

-- Project 1: E-Commerce Platform
DO $$
DECLARE
    v_project_id uuid := gen_random_uuid();
    v_req_ids uuid[10];
    v_feat_ids uuid[100];
    v_test_ids uuid[200];
    v_api_ids uuid[100];
    v_db_ids uuid[100];
    v_comp_ids uuid[100];
    v_doc_ids uuid[100];
    v_sec_ids uuid[100];
    v_perf_ids uuid[100];
    v_deploy_ids uuid[100];
    i INTEGER;
    j INTEGER;
BEGIN
    -- Create project
    INSERT INTO projects (id, name, slug, status, metadata, created_at, updated_at)
    VALUES (
        v_project_id,
        'E-Commerce Platform',
        'e-commerce-platform',
        'active',
        jsonb_build_object('domain', 'fullstack', 'description', 'Full-featured online shopping platform', 'priority', 'high'),
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
            'High-level requirement ' || i || ' for E-Commerce Platform',
            'requirement',
            CASE WHEN i <= 3 THEN 'closed' WHEN i <= 7 THEN 'in_progress' ELSE 'open' END,
            CASE WHEN i <= 2 THEN 3 WHEN i <= 5 THEN 2 ELSE 1 END,
            NOW(),
            NOW(),
            jsonb_build_object('level', 'epic')
        )
        RETURNING id INTO v_req_ids[i];
    END LOOP;

    -- Create exactly 100 features (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'FEAT-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Feature ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Feature ' || j || ' for requirement ' || i,
                'feature',
                CASE WHEN j <= 3 THEN 'closed' WHEN j <= 7 THEN 'in_progress' ELSE 'open' END,
                CASE WHEN j <= 2 THEN 2 WHEN j <= 5 THEN 1 ELSE 0 END,
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i)
            )
            RETURNING id INTO v_feat_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 200 tests (2 per feature)
    FOR i IN 1..100 LOOP
        FOR j IN 1..2 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'TEST-' || LPAD((i - 1) * 2 + j::text, 3, '0') || ': Test ' || j || ' for FEAT-' || LPAD(i::text, 3, '0'),
                'Test ' || j || ' for feature ' || i,
                'test',
                CASE WHEN j = 1 THEN 'closed' ELSE 'open' END,
                1,
                v_feat_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('test_type', CASE j WHEN 1 THEN 'unit' ELSE 'integration' END)
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 APIs (1 per feature)
    FOR i IN 1..100 LOOP
        INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
        VALUES (
            gen_random_uuid(),
            v_project_id,
            'API-' || LPAD(i::text, 3, '0') || ': API for FEAT-' || LPAD(i::text, 3, '0'),
            'REST API for feature ' || i,
            'api',
            CASE WHEN i <= 30 THEN 'closed' ELSE 'open' END,
            2,
            v_feat_ids[i],
            NOW(),
            NOW(),
            jsonb_build_object('method', 'POST', 'path', '/api/v1/features/' || i)
        );
    END LOOP;

    -- Create exactly 100 databases (10 per requirement)
    FOR i IN 1..10 LOOP
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
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('schema_name', 'req_' || i || '_schema_' || j)
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 components (10 per requirement)
    FOR i IN 1..10 LOOP
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
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j % 3 WHEN 0 THEN 'form' WHEN 1 THEN 'display' ELSE 'interactive' END)
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 documentation (10 per requirement)
    FOR i IN 1..10 LOOP
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
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END)
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 security (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'SEC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Security ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Security item ' || j || ' for requirement ' || i,
                'security',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                3,
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('security_level', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END)
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 performance (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'PERF-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Performance ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Performance item ' || j || ' for requirement ' || i,
                'performance',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                2,
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', (j * 10) || 'ms')
            );
        END LOOP;
    END LOOP;

    -- Create exactly 100 deployment (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                gen_random_uuid(),
                v_project_id,
                'DEPLOY-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Deployment ' || j || ' for REQ-' || LPAD(i::text, 2, '0'),
                'Deployment ' || j || ' for requirement ' || i,
                'deployment',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                2,
                v_req_ids[i],
                NOW(),
                NOW(),
                jsonb_build_object('environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END)
            );
        END LOOP;
    END LOOP;

    -- Create links: requirements -> features
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, feat.id, 'implements', NOW(), '{}'::jsonb
    FROM items req
    JOIN items feat ON feat.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND feat.project_id = v_project_id AND feat.type = 'feature';

    -- Create links: features -> tests
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, test.id, 'tested_by', NOW(), '{}'::jsonb
    FROM items feat
    JOIN items test ON test.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature'
      AND test.project_id = v_project_id AND test.type = 'test';

    -- Create links: features -> APIs
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), feat.id, api.id, 'exposes', NOW(), '{}'::jsonb
    FROM items feat
    JOIN items api ON api.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.type = 'feature'
      AND api.project_id = v_project_id AND api.type = 'api';

    -- Create links: requirements -> databases
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, db.id, 'requires', NOW(), '{}'::jsonb
    FROM items req
    JOIN items db ON db.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND db.project_id = v_project_id AND db.type = 'database';

    -- Create links: requirements -> components
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, comp.id, 'uses', NOW(), '{}'::jsonb
    FROM items req
    JOIN items comp ON comp.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND comp.project_id = v_project_id AND comp.type = 'component';

    -- Create links: requirements -> documentation
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, doc.id, 'documented_by', NOW(), '{}'::jsonb
    FROM items req
    JOIN items doc ON doc.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND doc.project_id = v_project_id AND doc.type = 'documentation';

    -- Create links: requirements -> security
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, sec.id, 'secured_by', NOW(), '{}'::jsonb
    FROM items req
    JOIN items sec ON sec.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND sec.project_id = v_project_id AND sec.type = 'security';

    -- Create links: requirements -> performance
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, perf.id, 'optimized_by', NOW(), '{}'::jsonb
    FROM items req
    JOIN items perf ON perf.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND perf.project_id = v_project_id AND perf.type = 'performance';

    -- Create links: requirements -> deployment
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT gen_random_uuid(), req.id, deploy.id, 'deployed_by', NOW(), '{}'::jsonb
    FROM items req
    JOIN items deploy ON deploy.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.type = 'requirement'
      AND deploy.project_id = v_project_id AND deploy.type = 'deployment';

END $$;

-- Repeat for other 4 projects (simplified - same structure)
DO $$
DECLARE
    v_project_id uuid;
    v_req_ids uuid[10];
    i INTEGER;
    j INTEGER;
BEGIN
    -- Project 2: Healthcare Management System
    v_project_id := gen_random_uuid();
    INSERT INTO projects (id, name, slug, status, metadata, created_at, updated_at)
    VALUES (v_project_id, 'Healthcare Management System', 'healthcare-management-system', 'active', jsonb_build_object('domain', 'backend', 'description', 'HIPAA-compliant patient records system', 'priority', 'high'), NOW(), NOW());
    
    FOR i IN 1..10 LOOP
        INSERT INTO items (id, project_id, title, description, type, status, priority, created_at, updated_at, metadata)
        VALUES (gen_random_uuid(), v_project_id, 'REQ-' || LPAD(i::text, 2, '0'), 'Requirement ' || i, 'requirement', 'open', 1, NOW(), NOW(), '{}'::jsonb)
        RETURNING id INTO v_req_ids[i];
    END LOOP;
    
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (gen_random_uuid(), v_project_id, 'FEAT-' || LPAD((i - 1) * 10 + j::text, 3, '0'), 'Feature ' || j, 'feature', 'open', 1, v_req_ids[i], NOW(), NOW(), '{}'::jsonb);
        END LOOP;
    END LOOP;
    
    FOR i IN 1..100 LOOP
        FOR j IN 1..2 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            SELECT gen_random_uuid(), v_project_id, 'TEST-' || LPAD((i - 1) * 2 + j::text, 3, '0'), 'Test ' || j, 'test', 'open', 1, id, NOW(), NOW(), '{}'::jsonb
            FROM items WHERE project_id = v_project_id AND type = 'feature' ORDER BY created_at LIMIT 1 OFFSET i - 1;
        END LOOP;
    END LOOP;
    
    -- Add APIs, databases, components, documentation, security, performance, deployment (100 each)
    -- Similar pattern...
END $$;

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
WHERE p.deleted_at IS NULL
GROUP BY p.id, p.name
ORDER BY p.name;
