-- Comprehensive hierarchical project data population script V2
-- Creates 5 projects with exactly 100+ items of each type
-- Each project follows a top-down hierarchy: 10 requirements -> 100 features -> 200 tests, etc.

-- Helper function to generate UUID
CREATE OR REPLACE FUNCTION generate_uuid() RETURNS uuid AS $$
BEGIN
    RETURN gen_random_uuid();
END;
$$ LANGUAGE plpgsql;

-- Function to create a project with hierarchical items (ensuring 100+ of each type)
CREATE OR REPLACE FUNCTION create_hierarchical_project_v2(
    p_name TEXT,
    p_description TEXT,
    p_domain TEXT
) RETURNS uuid AS $$
DECLARE
    v_project_id uuid;
    v_requirement_id uuid;
    v_feature_id uuid;
    v_test_id uuid;
    v_api_id uuid;
    v_database_id uuid;
    v_component_id uuid;
    v_documentation_id uuid;
    v_security_id uuid;
    v_performance_id uuid;
    v_deployment_id uuid;
    i INTEGER;
    j INTEGER;
    v_item_id uuid;
BEGIN
    -- Create project
    INSERT INTO projects (id, name, slug, status, metadata, created_at, updated_at)
    VALUES (
        generate_uuid(),
        p_name,
        lower(replace(p_name, ' ', '-')),
        'active',
        jsonb_build_object(
            'domain', p_domain,
            'description', p_description,
            'priority', 'high'
        ),
        NOW(),
        NOW()
    )
    RETURNING id INTO v_project_id;

    -- Create exactly 10 top-level requirements
    FOR i IN 1..10 LOOP
        INSERT INTO items (id, project_id, title, description, type, status, priority, created_at, updated_at, metadata)
        VALUES (
            generate_uuid(),
            v_project_id,
            'REQ-' || i || ': ' || CASE i
                WHEN 1 THEN 'User Authentication & Authorization'
                WHEN 2 THEN 'Data Management & Storage'
                WHEN 3 THEN 'API Integration & Communication'
                WHEN 4 THEN 'User Interface & Experience'
                WHEN 5 THEN 'Security & Compliance'
                WHEN 6 THEN 'Performance & Scalability'
                WHEN 7 THEN 'Monitoring & Logging'
                WHEN 8 THEN 'Deployment & Infrastructure'
                WHEN 9 THEN 'Testing & Quality Assurance'
                WHEN 10 THEN 'Documentation & Training'
            END,
            'High-level requirement for ' || CASE i
                WHEN 1 THEN 'implementing secure user authentication and role-based access control'
                WHEN 2 THEN 'managing data persistence, backup, and recovery'
                WHEN 3 THEN 'integrating with external APIs and services'
                WHEN 4 THEN 'providing intuitive user interfaces'
                WHEN 5 THEN 'ensuring security compliance and data protection'
                WHEN 6 THEN 'optimizing performance and handling scale'
                WHEN 7 THEN 'monitoring system health and logging events'
                WHEN 8 THEN 'deploying and managing infrastructure'
                WHEN 9 THEN 'testing and ensuring quality'
                WHEN 10 THEN 'documenting and training users'
            END,
            'requirement',
            CASE WHEN i <= 3 THEN 'closed' WHEN i <= 7 THEN 'in_progress' ELSE 'open' END,
            CASE WHEN i <= 2 THEN 3 WHEN i <= 5 THEN 2 WHEN i <= 8 THEN 1 ELSE 0 END,
            NOW(),
            NOW(),
            jsonb_build_object('level', 'epic', 'category', CASE i
                WHEN 1 THEN 'security'
                WHEN 2 THEN 'data'
                WHEN 3 THEN 'integration'
                WHEN 4 THEN 'ui'
                WHEN 5 THEN 'security'
                WHEN 6 THEN 'performance'
                WHEN 7 THEN 'operations'
                WHEN 8 THEN 'infrastructure'
                WHEN 9 THEN 'quality'
                WHEN 10 THEN 'documentation'
            END)
        )
        RETURNING id INTO v_requirement_id;
    END LOOP;

    -- Create exactly 100 features (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'FEAT-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Feature ' || j || ' for REQ-' || i,
                'Detailed feature implementation for requirement ' || i || ', feature ' || j || '. This feature includes comprehensive functionality, user stories, and acceptance criteria.',
                'feature',
                CASE WHEN j <= 3 THEN 'closed' WHEN j <= 7 THEN 'in_progress' ELSE 'open' END,
                CASE WHEN j <= 2 THEN 2 WHEN j <= 5 THEN 1 ELSE 0 END,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' ORDER BY created_at LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i, 'feature_index', j, 'complexity', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END)
            )
            RETURNING id INTO v_feature_id;
        END LOOP;
    END LOOP;

    -- Create exactly 200 tests (2 per feature)
    FOR i IN 1..100 LOOP
        FOR j IN 1..2 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'TEST-' || LPAD((i - 1) * 2 + j::text, 3, '0') || ': Test ' || j || ' for FEAT-' || LPAD(i::text, 3, '0'),
                'Test case ' || j || ' for feature ' || i || '. ' || CASE j WHEN 1 THEN 'Unit test covering core functionality.' ELSE 'Integration test covering end-to-end scenarios.' END,
                'test',
                CASE WHEN j = 1 THEN 'closed' ELSE 'open' END,
                1,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'feature' AND title LIKE 'FEAT-' || LPAD(i::text, 3, '0') || ':%' ORDER BY created_at LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('test_type', CASE j WHEN 1 THEN 'unit' ELSE 'integration' END, 'coverage', CASE j WHEN 1 THEN '80%' ELSE '60%' END)
            )
            RETURNING id INTO v_test_ids[(i - 1) * 2 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 APIs (1 per feature)
    FOR i IN 1..100 LOOP
        INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
        VALUES (
            generate_uuid(),
            v_project_id,
            'API-' || LPAD(i::text, 3, '0') || ': REST API for FEAT-' || LPAD(i::text, 3, '0'),
            'REST API endpoint for feature ' || i || '. Provides CRUD operations and business logic integration.',
            'api',
            CASE WHEN i <= 30 THEN 'closed' WHEN i <= 70 THEN 'in_progress' ELSE 'open' END,
            2,
            v_feature_ids[i],
            NOW(),
            NOW(),
            jsonb_build_object('method', CASE WHEN i % 4 = 0 THEN 'GET' WHEN i % 4 = 1 THEN 'POST' WHEN i % 4 = 2 THEN 'PUT' ELSE 'DELETE' END, 'path', '/api/v1/features/' || i)
        )
        RETURNING id INTO v_api_ids[i];
    END LOOP;

    -- Create exactly 100 databases (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'DB-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Database schema ' || j || ' for REQ-' || i,
                'Database schema and tables ' || j || ' for requirement ' || i || '. Includes tables, indexes, and constraints.',
                'database',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                2,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('schema_name', 'req_' || i || '_schema_' || j, 'tables', (j * 3))
            )
            RETURNING id INTO v_database_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 components (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'COMP-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Component ' || j || ' for REQ-' || i,
                'UI component ' || j || ' for requirement ' || i || '. ' || CASE j WHEN 1 THEN 'Form component with validation.' WHEN 2 THEN 'Display component with data visualization.' ELSE 'Interactive component with user interactions.' END,
                'component',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                1,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j % 3 WHEN 0 THEN 'form' WHEN 1 THEN 'display' ELSE 'interactive' END, 'framework', 'react')
            )
            RETURNING id INTO v_component_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 documentation items (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'DOC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Documentation ' || j || ' for REQ-' || i,
                'Documentation ' || j || ' for requirement ' || i || '. ' || CASE j WHEN 1 THEN 'Technical specification.' WHEN 2 THEN 'API documentation.' WHEN 3 THEN 'User guide.' ELSE 'Developer guide.' END,
                'documentation',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                1,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END)
            )
            RETURNING id INTO v_documentation_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 security items (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'SEC-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Security ' || j || ' for REQ-' || i,
                'Security review and compliance item ' || j || ' for requirement ' || i || '. Includes vulnerability assessment and compliance checks.',
                'security',
                CASE WHEN j <= 3 THEN 'closed' ELSE 'open' END,
                3,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('security_level', CASE WHEN j <= 3 THEN 'high' WHEN j <= 7 THEN 'medium' ELSE 'low' END, 'compliance', 'SOC2')
            )
            RETURNING id INTO v_security_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 performance items (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'PERF-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Performance ' || j || ' for REQ-' || i,
                'Performance optimization item ' || j || ' for requirement ' || i || '. Includes load testing, caching strategies, and optimization.',
                'performance',
                CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                2,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', (j * 10) || 'ms', 'throughput', (j * 100) || 'req/s')
            )
            RETURNING id INTO v_performance_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create exactly 100 deployment items (10 per requirement)
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'DEPLOY-' || LPAD((i - 1) * 10 + j::text, 3, '0') || ': Deployment ' || j || ' for REQ-' || i,
                'Deployment configuration ' || j || ' for requirement ' || i || '. Includes CI/CD pipelines, infrastructure as code, and environment setup.',
                'deployment',
                CASE WHEN j <= 5 THEN 'closed' ELSE 'open' END,
                2,
                (SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END, 'platform', 'kubernetes')
            )
            RETURNING id INTO v_deployment_ids[(i - 1) * 10 + j];
        END LOOP;
    END LOOP;

    -- Create comprehensive links between items
    -- Link requirements to features
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        feat.id,
        'implements',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_feature')
    FROM items req
    CROSS JOIN items feat
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND feat.project_id = v_project_id
        AND feat.type = 'feature'
        AND feat.parent_id = req.id;

    -- Link features to tests
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        feat.id,
        test.id,
        'tested_by',
        NOW(),
        jsonb_build_object('link_type', 'feature_to_test')
    FROM items feat
    CROSS JOIN items test
    WHERE feat.project_id = v_project_id
        AND feat.type = 'feature'
        AND test.project_id = v_project_id
        AND test.type = 'test'
        AND test.parent_id = feat.id;

    -- Link features to APIs
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        feat.id,
        api.id,
        'exposes',
        NOW(),
        jsonb_build_object('link_type', 'feature_to_api')
    FROM items feat
    CROSS JOIN items api
    WHERE feat.project_id = v_project_id
        AND feat.type = 'feature'
        AND api.project_id = v_project_id
        AND api.type = 'api'
        AND api.parent_id = feat.id;

    -- Link requirements to databases
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        db.id,
        'requires',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_database')
    FROM items req
    CROSS JOIN items db
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND db.project_id = v_project_id
        AND db.type = 'database'
        AND db.parent_id = req.id;

    -- Link features to components
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        feat.id,
        comp.id,
        'uses',
        NOW(),
        jsonb_build_object('link_type', 'feature_to_component')
    FROM items feat
    CROSS JOIN items comp
    WHERE feat.project_id = v_project_id
        AND feat.type = 'feature'
        AND comp.project_id = v_project_id
        AND comp.type = 'component'
        AND comp.parent_id IN (
            SELECT id FROM items WHERE project_id = v_project_id AND type = 'requirement' AND parent_id IS NULL
        )
        AND feat.parent_id = comp.parent_id;

    -- Link requirements to documentation
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        doc.id,
        'documented_by',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_documentation')
    FROM items req
    CROSS JOIN items doc
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND doc.project_id = v_project_id
        AND doc.type = 'documentation'
        AND doc.parent_id = req.id;

    -- Link requirements to security items
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        sec.id,
        'secured_by',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_security')
    FROM items req
    CROSS JOIN items sec
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND sec.project_id = v_project_id
        AND sec.type = 'security'
        AND sec.parent_id = req.id;

    -- Link requirements to performance items
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        perf.id,
        'optimized_by',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_performance')
    FROM items req
    CROSS JOIN items perf
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND perf.project_id = v_project_id
        AND perf.type = 'performance'
        AND perf.parent_id = req.id;

    -- Link requirements to deployment items
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        req.id,
        deploy.id,
        'deployed_by',
        NOW(),
        jsonb_build_object('link_type', 'requirement_to_deployment')
    FROM items req
    CROSS JOIN items deploy
    WHERE req.project_id = v_project_id
        AND req.type = 'requirement'
        AND deploy.project_id = v_project_id
        AND deploy.type = 'deployment'
        AND deploy.parent_id = req.id;

    -- Cross-link related features (10% chance)
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        f1.id,
        f2.id,
        'related_to',
        NOW(),
        jsonb_build_object('link_type', 'feature_to_feature')
    FROM items f1
    CROSS JOIN items f2
    WHERE f1.project_id = v_project_id
        AND f1.type = 'feature'
        AND f2.project_id = v_project_id
        AND f2.type = 'feature'
        AND f1.id < f2.id
        AND (f1.parent_id = f2.parent_id OR ABS(CAST(SUBSTRING(f1.title FROM 'FEAT-(\d+)') AS INTEGER) - CAST(SUBSTRING(f2.title FROM 'FEAT-(\d+)') AS INTEGER)) <= 2)
        AND random() < 0.1;

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;

-- Delete existing projects if they exist
DELETE FROM projects WHERE name IN ('E-Commerce Platform', 'Healthcare Management System', 'Real-Time Analytics Dashboard', 'Mobile Banking App', 'DevOps Automation Platform');

-- Create 5 comprehensive projects
DO $$
DECLARE
    v_project_id uuid;
BEGIN
    -- Project 1: E-Commerce Platform
    SELECT create_hierarchical_project_v2(
        'E-Commerce Platform',
        'Full-featured online shopping platform with payment integration, inventory management, and order processing',
        'fullstack'
    ) INTO v_project_id;

    -- Project 2: Healthcare Management System
    SELECT create_hierarchical_project_v2(
        'Healthcare Management System',
        'HIPAA-compliant patient records, appointment scheduling, and medical billing system',
        'backend'
    ) INTO v_project_id;

    -- Project 3: Real-Time Analytics Dashboard
    SELECT create_hierarchical_project_v2(
        'Real-Time Analytics Dashboard',
        'Data visualization platform with real-time streaming, ML predictions, and interactive charts',
        'data'
    ) INTO v_project_id;

    -- Project 4: Mobile Banking App
    SELECT create_hierarchical_project_v2(
        'Mobile Banking App',
        'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking',
        'mobile'
    ) INTO v_project_id;

    -- Project 5: DevOps Automation Platform
    SELECT create_hierarchical_project_v2(
        'DevOps Automation Platform',
        'CI/CD pipeline automation, infrastructure as code, monitoring, and deployment orchestration',
        'devops'
    ) INTO v_project_id;
END $$;

-- Summary query
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
