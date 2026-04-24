-- Comprehensive hierarchical project data population script
-- Creates 5 projects with 100+ items of each type (requirement, feature, test, etc.)
-- Each project follows a top-down hierarchy with proper relationships

-- Helper function to generate UUID
CREATE OR REPLACE FUNCTION generate_uuid() RETURNS uuid AS $$
BEGIN
    RETURN gen_random_uuid();
END;
$$ LANGUAGE plpgsql;

-- Function to create a project with hierarchical items
CREATE OR REPLACE FUNCTION create_hierarchical_project(
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
    v_item_id uuid;
    v_parent_id uuid;
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

    -- Create top-level requirements (10 main requirements)
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

        -- Store first requirement ID for linking
        IF i = 1 THEN
            v_requirement_id := v_requirement_id;
        END IF;

        -- Create features under each requirement (10 features per requirement = 100 features)
        FOR j IN 1..10 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'FEAT-' || (i * 10 + j) || ': Feature for REQ-' || i,
                'Detailed feature implementation for requirement ' || i || ', feature ' || j,
                'feature',
                CASE WHEN j <= 3 THEN 'closed' WHEN j <= 7 THEN 'in_progress' ELSE 'open' END,
                CASE WHEN j <= 2 THEN 2 WHEN j <= 5 THEN 1 ELSE 0 END,
                (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('requirement_id', i, 'feature_index', j)
            )
            RETURNING id INTO v_feature_id;

            -- Store first feature ID for linking
            IF i = 1 AND j = 1 THEN
                v_feature_id := v_feature_id;
            END IF;

            -- Create tests for each feature (2 tests per feature = 200 tests)
            FOR k IN 1..2 LOOP
                INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
                VALUES (
                    generate_uuid(),
                    v_project_id,
                    'TEST-' || (i * 100 + j * 10 + k) || ': Test for FEAT-' || (i * 10 + j),
                    'Test case for feature ' || (i * 10 + j) || ', test ' || k,
                    'test',
                    CASE WHEN k = 1 THEN 'closed' ELSE 'open' END,
                    1,
                    v_feature_id,
                    NOW(),
                    NOW(),
                    jsonb_build_object('test_type', CASE k WHEN 1 THEN 'unit' ELSE 'integration' END)
                );
            END LOOP;

            -- Create API endpoints for features (1 API per 2 features = 50 APIs)
            IF j % 2 = 0 THEN
                INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
                VALUES (
                    generate_uuid(),
                    v_project_id,
                    'API-' || (i * 5 + j / 2) || ': API for FEAT-' || (i * 10 + j),
                    'REST API endpoint for feature ' || (i * 10 + j),
                    'api',
                    CASE WHEN j <= 4 THEN 'closed' ELSE 'open' END,
                    2,
                    v_feature_id,
                    NOW(),
                    NOW(),
                    jsonb_build_object('method', 'POST', 'path', '/api/v1/features/' || (i * 10 + j))
                )
                RETURNING id INTO v_api_id;
            END IF;
        END LOOP;

        -- Create database schemas for requirements (1 per requirement = 10 databases)
        INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
        VALUES (
            generate_uuid(),
            v_project_id,
            'DB-' || i || ': Database schema for REQ-' || i,
            'Database schema and tables for requirement ' || i,
            'database',
            CASE WHEN i <= 3 THEN 'closed' ELSE 'open' END,
            2,
            (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
            NOW(),
            NOW(),
            jsonb_build_object('schema_name', 'req_' || i)
        )
        RETURNING id INTO v_database_id;

        -- Create components for requirements (2 per requirement = 20 components)
        FOR j IN 1..2 LOOP
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'COMP-' || (i * 2 + j - 2) || ': Component for REQ-' || i,
                'UI component for requirement ' || i || ', component ' || j,
                'component',
                CASE WHEN j = 1 THEN 'closed' ELSE 'open' END,
                1,
                (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('component_type', CASE j WHEN 1 THEN 'form' ELSE 'display' END)
            )
            RETURNING id INTO v_component_id;
        END LOOP;

        -- Create documentation for requirements (1 per requirement = 10 documentation)
        INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
        VALUES (
            generate_uuid(),
            v_project_id,
            'DOC-' || i || ': Documentation for REQ-' || i,
            'Technical documentation for requirement ' || i,
            'documentation',
            CASE WHEN i <= 5 THEN 'closed' ELSE 'open' END,
            1,
            (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
            NOW(),
            NOW(),
            jsonb_build_object('doc_type', 'technical_spec')
        )
        RETURNING id INTO v_documentation_id;

        -- Create security items (1 per 2 requirements = 5 security)
        IF i % 2 = 0 THEN
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'SEC-' || (i / 2) || ': Security for REQ-' || i,
                'Security review and compliance for requirement ' || i,
                'security',
                'open',
                3,
                (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('security_level', 'high')
            )
            RETURNING id INTO v_security_id;
        END IF;

        -- Create performance items (1 per 3 requirements = 3 performance)
        IF i % 3 = 0 THEN
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'PERF-' || (i / 3) || ': Performance for REQ-' || i,
                'Performance optimization for requirement ' || i,
                'performance',
                'open',
                2,
                (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('target_latency', '100ms')
            )
            RETURNING id INTO v_performance_id;
        END IF;

        -- Create deployment items (1 per 5 requirements = 2 deployment)
        IF i % 5 = 0 THEN
            INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, created_at, updated_at, metadata)
            VALUES (
                generate_uuid(),
                v_project_id,
                'DEPLOY-' || (i / 5) || ': Deployment for REQ-' || i,
                'Deployment configuration for requirement ' || i,
                'deployment',
                'open',
                2,
                (SELECT id FROM items WHERE project_id = v_project_id AND title LIKE 'REQ-' || i || ':%' LIMIT 1),
                NOW(),
                NOW(),
                jsonb_build_object('environment', 'production')
            )
            RETURNING id INTO v_deployment_id;
        END IF;
    END LOOP;

    -- Create links between items (comprehensive traceability)
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
        );

    -- Cross-link related features
    INSERT INTO links (id, source_id, target_id, link_type, created_at, metadata)
    SELECT
        generate_uuid(),
        f1.id,
        f2.id,
        'related_to',
        NOW(),
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
        AND random() < 0.1; -- 10% chance of cross-linking

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;

-- Create 5 comprehensive projects
DO $$
DECLARE
    v_project_id uuid;
BEGIN
    -- Project 1: E-Commerce Platform
    SELECT create_hierarchical_project(
        'E-Commerce Platform',
        'Full-featured online shopping platform with payment integration, inventory management, and order processing',
        'fullstack'
    ) INTO v_project_id;

    -- Project 2: Healthcare Management System
    SELECT create_hierarchical_project(
        'Healthcare Management System',
        'HIPAA-compliant patient records, appointment scheduling, and medical billing system',
        'backend'
    ) INTO v_project_id;

    -- Project 3: Real-Time Analytics Dashboard
    SELECT create_hierarchical_project(
        'Real-Time Analytics Dashboard',
        'Data visualization platform with real-time streaming, ML predictions, and interactive charts',
        'data'
    ) INTO v_project_id;

    -- Project 4: Mobile Banking App
    SELECT create_hierarchical_project(
        'Mobile Banking App',
        'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking',
        'mobile'
    ) INTO v_project_id;

    -- Project 5: DevOps Automation Platform
    SELECT create_hierarchical_project(
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
