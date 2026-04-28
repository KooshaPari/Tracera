#!/usr/bin/env python3
"""Create links between UI/UX items and SwiftRide features, user stories, and requirements."""

from pathlib import Path

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

# Link types for UI/UX relationships
LINK_TYPES = {
    "implements": "UI implements functionality",
    "enables": "UI enables user story",
    "satisfies": "UI satisfies requirement",
    "complies_with": "UI complies with accessibility",
    "uses": "Component uses design token",
    "contains": "Wireframe contains component",
    "follows": "UI follows pattern",
    "requires": "UI requires interaction capability",
}


def generate_linking_queries() -> None:
    """Generate SQL to create links between UI/UX items and existing items."""
    queries = []

    queries.append("-- ========================================")
    queries.append("-- Link UI/UX Items to Features, Stories, and Requirements")
    queries.append("-- ========================================")
    queries.append("BEGIN;")
    queries.append("")

    # 1. Link Wireframes to Features (wireframes implement features)
    queries.append("-- Link Driver App Wireframes to Driver Features")
    queries.append(f"""
WITH driver_wireframes AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'wireframe'
    AND metadata->>'app' = 'driver'
    AND tags && ARRAY['swiftride', 'ui-ux']
    ORDER BY created_at DESC
    LIMIT 35
),
driver_features AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'feature'
    AND (title ILIKE '%driver%' OR title ILIKE '%onboarding%' OR title ILIKE '%matching%')
    LIMIT 20
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    w.id,
    f.id,
    'implements',
    jsonb_build_object('relationship', 'wireframe implements feature', 'auto_linked', true),
    NOW()
FROM driver_wireframes w
CROSS JOIN LATERAL (
    SELECT id, title FROM driver_features ORDER BY RANDOM() LIMIT 2
) f
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Rider App Wireframes to Rider Features")
    queries.append(f"""
WITH rider_wireframes AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'wireframe'
    AND metadata->>'app' = 'rider'
    AND tags && ARRAY['swiftride', 'ui-ux']
    ORDER BY created_at DESC
    LIMIT 35
),
rider_features AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'feature'
    AND (title ILIKE '%rider%' OR title ILIKE '%payment%' OR title ILIKE '%booking%')
    LIMIT 20
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    w.id,
    f.id,
    'implements',
    jsonb_build_object('relationship', 'wireframe implements feature', 'auto_linked', true),
    NOW()
FROM rider_wireframes w
CROSS JOIN LATERAL (
    SELECT id, title FROM rider_features ORDER BY RANDOM() LIMIT 2
) f
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Admin Wireframes to Admin Features")
    queries.append(f"""
WITH admin_wireframes AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'wireframe'
    AND metadata->>'app' = 'admin'
    AND tags && ARRAY['swiftride', 'ui-ux']
    ORDER BY created_at DESC
    LIMIT 30
),
admin_features AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'feature'
    AND (title ILIKE '%admin%' OR title ILIKE '%monitoring%' OR title ILIKE '%dashboard%' OR title ILIKE '%analytics%')
    LIMIT 15
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    w.id,
    f.id,
    'implements',
    jsonb_build_object('relationship', 'wireframe implements feature', 'auto_linked', true),
    NOW()
FROM admin_wireframes w
CROSS JOIN LATERAL (
    SELECT id, title FROM admin_features ORDER BY RANDOM() LIMIT 2
) f
ON CONFLICT DO NOTHING;
""")

    # 2. Link Components to Features
    queries.append("")
    queries.append("-- Link Map Components to Location Features")
    queries.append(f"""
WITH map_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND metadata->>'category' = 'map'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
location_features AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'feature'
    AND (title ILIKE '%matching%' OR title ILIKE '%tracking%' OR title ILIKE '%navigation%')
    LIMIT 10
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    f.id,
    'implements',
    jsonb_build_object('relationship', 'component implements feature', 'category', 'map', 'auto_linked', true),
    NOW()
FROM map_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM location_features ORDER BY RANDOM() LIMIT 1
) f
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Payment Components to Payment Features")
    queries.append(f"""
WITH payment_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND metadata->>'category' = 'payment'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
payment_features AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'feature'
    AND title ILIKE '%payment%'
    LIMIT 5
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    f.id,
    'implements',
    jsonb_build_object('relationship', 'component implements feature', 'category', 'payment', 'auto_linked', true),
    NOW()
FROM payment_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM payment_features ORDER BY RANDOM() LIMIT 1
) f
ON CONFLICT DO NOTHING;
""")

    # 3. Link User Flows to User Stories
    queries.append("")
    queries.append("-- Link Rider User Flows to Rider User Stories")
    queries.append(f"""
WITH rider_flows AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'user_flow'
    AND metadata->>'user_type' = 'rider'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
rider_stories AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type IN ('user_story', 'story')
    AND (title ILIKE '%rider%' OR title ILIKE '%passenger%' OR title ILIKE '%book%')
    LIMIT 50
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    f.id,
    s.id,
    'enables',
    jsonb_build_object('relationship', 'flow enables user story', 'user_type', 'rider', 'auto_linked', true),
    NOW()
FROM rider_flows f
CROSS JOIN LATERAL (
    SELECT id, title FROM rider_stories ORDER BY RANDOM() LIMIT 2
) s
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Driver User Flows to Driver User Stories")
    queries.append(f"""
WITH driver_flows AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'user_flow'
    AND metadata->>'user_type' = 'driver'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
driver_stories AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type IN ('user_story', 'story')
    AND title ILIKE '%driver%'
    LIMIT 50
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    f.id,
    s.id,
    'enables',
    jsonb_build_object('relationship', 'flow enables user story', 'user_type', 'driver', 'auto_linked', true),
    NOW()
FROM driver_flows f
CROSS JOIN LATERAL (
    SELECT id, title FROM driver_stories ORDER BY RANDOM() LIMIT 2
) s
ON CONFLICT DO NOTHING;
""")

    # 4. Link Accessibility Requirements to Wireframes and Components
    queries.append("")
    queries.append("-- Link WCAG Requirements to All Wireframes")
    queries.append(f"""
WITH wcag_requirements AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'accessibility_requirement'
    AND (metadata->>'level' IN ('A', 'AA') OR metadata->>'category' = 'screen_reader')
    AND tags && ARRAY['swiftride', 'ui-ux']
),
all_wireframes AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'wireframe'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    w.id,
    a.id,
    'complies_with',
    jsonb_build_object('relationship', 'wireframe complies with accessibility', 'auto_linked', true),
    NOW()
FROM all_wireframes w
CROSS JOIN LATERAL (
    SELECT id, title FROM wcag_requirements ORDER BY RANDOM() LIMIT 3
) a
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Accessibility Requirements to Interactive Components")
    queries.append(f"""
WITH accessibility_reqs AS (
    SELECT id, title, metadata FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'accessibility_requirement'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
interactive_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND metadata->>'category' IN ('ui', 'navigation', 'input', 'ride', 'payment')
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    a.id,
    'complies_with',
    jsonb_build_object('relationship', 'component complies with accessibility', 'auto_linked', true),
    NOW()
FROM interactive_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM accessibility_reqs ORDER BY RANDOM() LIMIT 2
) a
ON CONFLICT DO NOTHING;
""")

    # 5. Link Components to Design Tokens
    queries.append("")
    queries.append("-- Link All Components to Design Tokens")
    queries.append(f"""
WITH color_tokens AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'design_token'
    AND metadata->>'category' = 'color'
    AND tags && ARRAY['swiftride', 'ui-ux']
    LIMIT 10
),
all_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    t.id,
    'uses',
    jsonb_build_object('relationship', 'component uses design token', 'token_type', 'color', 'auto_linked', true),
    NOW()
FROM all_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM color_tokens ORDER BY RANDOM() LIMIT 2
) t
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Components to Typography Tokens")
    queries.append(f"""
WITH typo_tokens AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'design_token'
    AND metadata->>'category' = 'typography'
    AND tags && ARRAY['swiftride', 'ui-ux']
    LIMIT 10
),
text_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    t.id,
    'uses',
    jsonb_build_object('relationship', 'component uses design token', 'token_type', 'typography', 'auto_linked', true),
    NOW()
FROM text_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM typo_tokens ORDER BY RANDOM() LIMIT 1
) t
ON CONFLICT DO NOTHING;
""")

    # 6. Link Wireframes to Components (wireframes contain components)
    queries.append("")
    queries.append("-- Link Wireframes to Their Components")
    queries.append(f"""
WITH all_wireframes AS (
    SELECT id, title, metadata FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'wireframe'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
all_components AS (
    SELECT id, title, metadata FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    w.id,
    c.id,
    'contains',
    jsonb_build_object('relationship', 'wireframe contains component', 'auto_linked', true),
    NOW()
FROM all_wireframes w
CROSS JOIN LATERAL (
    SELECT id, title FROM all_components ORDER BY RANDOM() LIMIT 5
) c
ON CONFLICT DO NOTHING;
""")

    # 7. Link UI Elements to UX Patterns
    queries.append("")
    queries.append("-- Link Components to UX Patterns They Follow")
    queries.append(f"""
WITH navigation_patterns AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'ux_pattern'
    AND metadata->>'category' = 'navigation'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
nav_components AS (
    SELECT id, title FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND metadata->>'category' = 'navigation'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    p.id,
    'follows',
    jsonb_build_object('relationship', 'component follows pattern', 'pattern_category', 'navigation', 'auto_linked', true),
    NOW()
FROM nav_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM navigation_patterns ORDER BY RANDOM() LIMIT 1
) p
ON CONFLICT DO NOTHING;
""")

    queries.append("-- Link Interactions to Components")
    queries.append(f"""
WITH all_interactions AS (
    SELECT id, title, metadata FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'interaction'
    AND tags && ARRAY['swiftride', 'ui-ux']
),
all_components AS (
    SELECT id, title, metadata FROM items
    WHERE project_id = '{PROJECT_ID}'
    AND type = 'component'
    AND tags && ARRAY['swiftride', 'ui-ux']
)
INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
SELECT
    gen_random_uuid(),
    c.id,
    i.id,
    'requires',
    jsonb_build_object('relationship', 'component requires interaction', 'auto_linked', true),
    NOW()
FROM all_components c
CROSS JOIN LATERAL (
    SELECT id, title FROM all_interactions ORDER BY RANDOM() LIMIT 2
) i
ON CONFLICT DO NOTHING;
""")

    queries.append("")
    queries.append("COMMIT;")
    queries.append("")
    queries.append("-- Verify link counts")
    queries.append(f"""
SELECT
    link_type,
    COUNT(*) as count
FROM links l
JOIN items source ON l.source_id = source.id
JOIN items target ON l.target_id = target.id
WHERE source.project_id = '{PROJECT_ID}'
  AND target.project_id = '{PROJECT_ID}'
  AND l.metadata->>'auto_linked' = 'true'
GROUP BY link_type
ORDER BY count DESC;
""")

    return "\n".join(queries)


def main() -> None:
    """Generate linking SQL file."""
    sql = generate_linking_queries()

    output_file = Path(__file__).resolve().parent.parent / "data" / "tmp" / "swiftride_uiux_links.sql"
    with output_file.open("w") as f:
        f.write(sql)


if __name__ == "__main__":
    main()
