-- SwiftRide Quality & Compliance Items
-- Project: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
-- Generated: 2026-01-31
-- Total Items: 570+

BEGIN;


-- ============================================
-- QUALITY GATES (60)
-- ============================================

INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
VALUES (
    '40e02d4d-bbc8-4608-b25d-d880d4f92766',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Unit Test Coverage >= 80%',
    'quality_gate',
    'All modules must maintain minimum 80% unit test coverage using pytest-cov.',
    'active',
    1,
    '{"gate_type":"coverage","threshold":80,"metric":"line_coverage"}'::jsonb,
    ARRAY{"coverage","unit-test","quality-gate"},
    NOW(),
    NOW()
);

INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
VALUES (
    '7d5bdbef-154f-45ad-8fa9-cce1c9a75fca',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Integration Test Coverage >= 70%',
    'quality_gate',
    'Integration tests must cover 70%+ of API endpoints.',
    'active',
    1,
    '{"gate_type":"coverage","threshold":70}'::jsonb,
    ARRAY{"coverage","integration"},
    NOW(),
    NOW()
);

INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
VALUES (
    '9acdfade-634b-4b00-86c5-082f0e6437b8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'E2E Test Coverage >= 60%',
    'quality_gate',
    'End-to-end tests must cover 60% of critical user journeys.',
    'active',
    2,
    '{"gate_type":"coverage","threshold":60}'::jsonb,
    ARRAY{"coverage","e2e"},
    NOW(),
    NOW()
);

INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
VALUES (
    '3f3452f2-fbe5-4ab6-8f52-e6255cc4aaab',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Branch Coverage >= 75%',
    'quality_gate',
    'All conditional branches must be tested with 75%+ coverage.',
    'active',
    2,
    '{"gate_type":"coverage","threshold":75}'::jsonb,
    ARRAY{"coverage","branch"},
    NOW(),
    NOW()
);

INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
VALUES (
    'a2e1f4b0-b431-40ad-b0f6-3c7673d627f6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Mutation Score >= 65%',
    'quality_gate',
    'Mutation testing score must be 65%+ to ensure test quality.',
    'active',
    3,
    '{"gate_type":"coverage","threshold":65}'::jsonb,
    ARRAY{"coverage","mutation"},
    NOW(),
    NOW()
);

COMMIT;
