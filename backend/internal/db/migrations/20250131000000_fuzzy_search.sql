-- Migration: Add PostgreSQL extensions for TraceRTM
-- Enables: fuzzy search, hierarchical data, security, performance monitoring

-- =============================================================================
-- PART 1: Enable Extensions
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SEARCH EXTENSIONS
-- ─────────────────────────────────────────────────────────────────────────────

-- pg_trgm: Trigram-based fuzzy text matching
-- Enables: % similarity operator, similarity(), word_similarity(), show_trgm()
-- Use case: Typo tolerance, "did you mean?" suggestions, fuzzy autocomplete
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- fuzzystrmatch: Phonetic matching and edit distance
-- Enables: soundex(), metaphone(), dmetaphone(), levenshtein(), levenshtein_less_equal()
-- Use case: Name matching, phonetic search ("Jon" matches "John")
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- unaccent: Accent/diacritic removal
-- Enables: unaccent() function for accent-insensitive search
-- Use case: "café" matches "cafe", "naïve" matches "naive"
CREATE EXTENSION IF NOT EXISTS unaccent;

-- pgvector: Vector similarity search (OPTIONAL - may not be available on all Supabase plans)
-- Enables: vector type, <=> cosine distance, <-> L2 distance, <#> inner product
-- Use case: Semantic/AI-powered search with VoyageAI embeddings
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'pgvector extension not available on this Supabase plan';
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- HIERARCHICAL DATA (Requirements Traceability)
-- ─────────────────────────────────────────────────────────────────────────────

-- ltree: Hierarchical tree-like structures
-- Enables: ltree type, @> ancestor, <@ descendant, ~ regex match, lca() common ancestor
-- Use case: Requirement hierarchies (REQ.1.2.3), folder paths, org structures
-- Example: WHERE path <@ 'REQ.SYSTEM.AUTH' (all children of AUTH requirement)
CREATE EXTENSION IF NOT EXISTS ltree;

-- ─────────────────────────────────────────────────────────────────────────────
-- INDEXING & PERFORMANCE
-- ─────────────────────────────────────────────────────────────────────────────

-- btree_gin: Index common types in GIN
-- Enables: GIN indexes on int, text, timestamp, etc (not just arrays/tsvector)
-- Use case: Multi-column GIN indexes for complex filter queries
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- pg_stat_statements: Query performance monitoring
-- Enables: Tracks execution stats for all SQL statements
-- Use case: Find slow queries, optimize indexes, monitor performance
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ─────────────────────────────────────────────────────────────────────────────
-- DATA TYPES & SECURITY
-- ─────────────────────────────────────────────────────────────────────────────

-- citext: Case-insensitive text type
-- Enables: citext column type that compares case-insensitively
-- Use case: Emails, usernames, tags where case shouldn't matter
CREATE EXTENSION IF NOT EXISTS citext;

-- pgcrypto: Cryptographic functions
-- Enables: gen_random_bytes(), crypt(), digest(), encrypt/decrypt
-- Use case: Secure password hashing, API key generation, data encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- uuid-ossp: UUID generation functions
-- Enables: uuid_generate_v1(), v4(), v5() and more options
-- Use case: Alternative UUID generation, namespaced UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- PART 2: Add search columns to items table if they don't exist
-- =============================================================================

-- Add search_vector column for full-text search
ALTER TABLE items
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Add embedding column for vector search (1024 dimensions for voyage-3.5)
-- This is conditional because pgvector may not be available on all Supabase plans
DO $$
BEGIN
    ALTER TABLE items
    ADD COLUMN IF NOT EXISTS embedding vector(1024);
EXCEPTION WHEN OTHERS THEN
    -- pgvector not available, skip this column
    NULL;
END $$;

-- Add type column if not exists
ALTER TABLE items
ADD COLUMN IF NOT EXISTS type varchar(50) NOT NULL DEFAULT 'requirement';

-- Add priority column if not exists
ALTER TABLE items
ADD COLUMN IF NOT EXISTS priority integer DEFAULT 0;

-- Add deleted_at for soft deletes
ALTER TABLE items
ADD COLUMN IF NOT EXISTS deleted_at timestamp;

-- Add hierarchical path for requirement traceability (ltree)
-- Example paths: 'REQ.SYSTEM.AUTH.LOGIN', 'SPEC.FUNC.USER_MGMT'
ALTER TABLE items
ADD COLUMN IF NOT EXISTS path ltree;

-- Add parent_id for tree structure (alternative to ltree, can coexist)
ALTER TABLE items
ADD COLUMN IF NOT EXISTS parent_id uuid REFERENCES items(id) ON DELETE SET NULL;

-- Add tags array for flexible categorization
ALTER TABLE items
ADD COLUMN IF NOT EXISTS tags text[] DEFAULT '{}';

-- =============================================================================
-- PART 3: Create unaccent text search configuration
-- =============================================================================

-- Create a custom text search configuration that removes accents
DO $$
BEGIN
    -- Create immutable unaccent function for indexing
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'immutable_unaccent'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        CREATE OR REPLACE FUNCTION public.immutable_unaccent(text)
        RETURNS text AS
        $func$
        SELECT unaccent($1)
        $func$ LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT;
    END IF;

    -- Create custom text search configuration with unaccent
    IF NOT EXISTS (
        SELECT 1 FROM pg_ts_config WHERE cfgname = 'english_unaccent'
    ) THEN
        CREATE TEXT SEARCH CONFIGURATION public.english_unaccent (COPY = english);
        ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
        ALTER MAPPING FOR hword, hword_part, word
        WITH unaccent, english_stem;
    END IF;
END $$;

-- =============================================================================
-- PART 4: Create function to generate search vector
-- =============================================================================

-- Create trigger function to generate search vector (if not already created)
-- Try to create - will fail silently if columns don't exist
DO $$
BEGIN
    EXECUTE 'CREATE OR REPLACE FUNCTION update_item_search_vector()
    RETURNS trigger AS $func$
    BEGIN
        NEW.search_vector :=
            setweight(to_tsvector(''public.english_unaccent'', coalesce(NEW.title, '''')), ''A'') ||
            setweight(to_tsvector(''public.english_unaccent'', coalesce(NEW.description, '''')), ''B'') ||
            setweight(to_tsvector(''public.english_unaccent'', coalesce(NEW.type, '''')), ''C'') ||
            setweight(to_tsvector(''public.english_unaccent'', coalesce(NEW.status, '''')), ''D'');
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql';
EXCEPTION WHEN OTHERS THEN
    NULL; -- Columns might not exist yet
END $$;

-- Create trigger to auto-update search_vector (if not already created)
DO $$
BEGIN
    DROP TRIGGER IF EXISTS items_search_vector_trigger ON items;
    EXECUTE 'CREATE TRIGGER items_search_vector_trigger
        BEFORE INSERT OR UPDATE OF title, description, type, status
        ON items
        FOR EACH ROW
        EXECUTE FUNCTION update_item_search_vector()';
EXCEPTION WHEN OTHERS THEN
    NULL; -- Trigger might not be creatable due to missing columns
END $$;

-- =============================================================================
-- PART 5: Create GIN indexes for full-text and trigram search
-- =============================================================================

-- Full-text search index (GIN is faster for search, updates are slower)
CREATE INDEX IF NOT EXISTS idx_items_search_vector
ON items USING GIN (search_vector);

-- Trigram indexes for fuzzy matching on title and description
-- These enable the % operator and similarity() function
-- Check if title column exists first
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_items_title_trgm
    ON items USING GIN (title gin_trgm_ops);
EXCEPTION WHEN OTHERS THEN
    NULL; -- Column might not exist yet
END $$;

-- Check if description column exists first
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_items_description_trgm
    ON items USING GIN (description gin_trgm_ops);
EXCEPTION WHEN OTHERS THEN
    NULL; -- Column might not exist yet
END $$;

-- Combined trigram index for both fields (more efficient for searches across both)
-- Only create if description column exists
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_items_title_desc_trgm
    ON items USING GIN ((title || ' ' || coalesce(description, '')) gin_trgm_ops);
EXCEPTION WHEN OTHERS THEN
    NULL; -- One or both columns might not exist yet
END $$;

-- =============================================================================
-- PART 6: Create hierarchical and array indexes
-- =============================================================================

-- GiST index for ltree path queries (ancestor/descendant lookups)
CREATE INDEX IF NOT EXISTS idx_items_path_gist
ON items USING GIST (path);

-- Btree index for ltree path exact matches and sorting
CREATE INDEX IF NOT EXISTS idx_items_path_btree
ON items USING BTREE (path);

-- Index for parent_id tree traversal
CREATE INDEX IF NOT EXISTS idx_items_parent_id
ON items (parent_id) WHERE parent_id IS NOT NULL;

-- GIN index for tags array (fast @> contains, && overlap queries)
CREATE INDEX IF NOT EXISTS idx_items_tags_gin
ON items USING GIN (tags);

-- =============================================================================
-- PART 7: Create vector search indexes (HNSW for approximate nearest neighbor)
-- =============================================================================

-- HNSW index for fast approximate nearest neighbor search (CONDITIONAL - requires pgvector)
-- m=16 (connections per layer), ef_construction=64 (build quality)
-- Using cosine distance (<=>)
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_items_embedding_hnsw
    ON items USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
EXCEPTION WHEN OTHERS THEN
    -- pgvector index not available, skip this index
    NULL;
END $$;

-- =============================================================================
-- PART 7: Add trigram indexes to projects table
-- =============================================================================

-- Create name index if name column exists
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_projects_name_trgm
    ON projects USING GIN (name gin_trgm_ops);
EXCEPTION WHEN OTHERS THEN
    NULL; -- Column might not exist
END $$;

-- Create description index if description column exists
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_projects_description_trgm
    ON projects USING GIN (description gin_trgm_ops);
EXCEPTION WHEN OTHERS THEN
    NULL; -- Column might not exist
END $$;

-- =============================================================================
-- PART 8: Create helper functions for fuzzy search
-- =============================================================================

-- Function to perform fuzzy search with typo tolerance
CREATE OR REPLACE FUNCTION fuzzy_search_items(
    search_query text,
    project_uuid uuid DEFAULT NULL,
    similarity_threshold float DEFAULT 0.3,
    max_results int DEFAULT 20
)
RETURNS TABLE (
    id uuid,
    project_id uuid,
    title varchar(255),
    description text,
    type varchar(50),
    status varchar(50),
    priority integer,
    similarity_score float,
    ts_rank float,
    combined_score float
) AS $$
BEGIN
    -- Set similarity threshold for this session
    PERFORM set_limit(similarity_threshold);

    RETURN QUERY
    SELECT
        i.id,
        i.project_id,
        i.title,
        i.description,
        i.type,
        i.status,
        i.priority,
        greatest(
            similarity(i.title, search_query),
            similarity(coalesce(i.description, ''), search_query)
        ) AS similarity_score,
        ts_rank(i.search_vector, plainto_tsquery('public.english_unaccent', search_query)) AS ts_rank,
        -- Combined score: 50% full-text rank, 50% similarity
        (
            0.5 * ts_rank(i.search_vector, plainto_tsquery('public.english_unaccent', search_query)) +
            0.5 * greatest(
                similarity(i.title, search_query),
                similarity(coalesce(i.description, ''), search_query)
            )
        ) AS combined_score
    FROM items i
    WHERE
        i.deleted_at IS NULL
        AND (project_uuid IS NULL OR i.project_id = project_uuid)
        AND (
            -- Full-text search match
            i.search_vector @@ plainto_tsquery('public.english_unaccent', search_query)
            OR
            -- Trigram similarity match (catches typos)
            i.title % search_query
            OR
            coalesce(i.description, '') % search_query
        )
    ORDER BY combined_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get search suggestions with typo tolerance
CREATE OR REPLACE FUNCTION search_suggestions(
    prefix text,
    project_uuid uuid DEFAULT NULL,
    max_suggestions int DEFAULT 10
)
RETURNS TABLE (
    suggestion text,
    similarity_score float
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (lower(i.title))
        i.title AS suggestion,
        word_similarity(prefix, i.title) AS similarity_score
    FROM items i
    WHERE
        i.deleted_at IS NULL
        AND (project_uuid IS NULL OR i.project_id = project_uuid)
        AND (
            i.title ILIKE prefix || '%'
            OR i.title % prefix
        )
    ORDER BY lower(i.title), similarity_score DESC
    LIMIT max_suggestions;
END;
$$ LANGUAGE plpgsql;

-- Function for phonetic search (matches similar-sounding words)
CREATE OR REPLACE FUNCTION phonetic_search_items(
    search_query text,
    project_uuid uuid DEFAULT NULL,
    max_results int DEFAULT 20
)
RETURNS TABLE (
    id uuid,
    project_id uuid,
    title varchar(255),
    description text,
    metaphone_match boolean,
    soundex_match boolean
) AS $$
DECLARE
    query_metaphone text;
    query_soundex text;
BEGIN
    -- Generate phonetic codes for the search query
    query_metaphone := metaphone(search_query, 10);
    query_soundex := soundex(search_query);

    RETURN QUERY
    SELECT
        i.id,
        i.project_id,
        i.title,
        i.description,
        metaphone(i.title, 10) = query_metaphone AS metaphone_match,
        soundex(i.title) = query_soundex AS soundex_match
    FROM items i
    WHERE
        i.deleted_at IS NULL
        AND (project_uuid IS NULL OR i.project_id = project_uuid)
        AND (
            metaphone(i.title, 10) = query_metaphone
            OR soundex(i.title) = query_soundex
        )
    ORDER BY
        CASE
            WHEN metaphone(i.title, 10) = query_metaphone THEN 1
            WHEN soundex(i.title) = query_soundex THEN 2
            ELSE 3
        END
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate edit distance (Levenshtein)
CREATE OR REPLACE FUNCTION typo_distance(str1 text, str2 text)
RETURNS integer AS $$
BEGIN
    RETURN levenshtein_less_equal(lower(str1), lower(str2), 3);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================================================
-- PART 9: Backfill search vectors for existing items
-- =============================================================================

-- Only backfill if all required columns exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'search_vector'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'title'
    ) THEN
        UPDATE items
        SET search_vector =
            setweight(to_tsvector('public.english_unaccent', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('public.english_unaccent', coalesce(description, '')), 'B') ||
            setweight(to_tsvector('public.english_unaccent', coalesce(type, '')), 'C') ||
            setweight(to_tsvector('public.english_unaccent', coalesce(status, '')), 'D')
        WHERE search_vector IS NULL;
    END IF;
END $$;

-- =============================================================================
-- PART 10: Create statistics view for search monitoring
-- =============================================================================

-- Create view that works with or without embedding column
DO $$
BEGIN
    EXECUTE 'CREATE OR REPLACE VIEW search_stats AS
    SELECT
        (SELECT count(*) FROM items WHERE search_vector IS NOT NULL) AS items_with_search_vector,
        COALESCE((SELECT count(*) FROM items WHERE embedding IS NOT NULL), 0) AS items_with_embedding,
        (SELECT count(*) FROM items WHERE deleted_at IS NULL) AS total_active_items,
        (SELECT pg_size_pretty(pg_total_relation_size(''items''))) AS items_table_size,
        COALESCE((SELECT pg_size_pretty(pg_relation_size(''idx_items_search_vector''))), ''0 bytes'') AS search_index_size,
        COALESCE((SELECT pg_size_pretty(pg_relation_size(''idx_items_title_trgm''))), ''0 bytes'') AS trgm_title_index_size,
        COALESCE((SELECT pg_size_pretty(pg_relation_size(''idx_items_embedding_hnsw''))), ''0 bytes'') AS vector_index_size';
EXCEPTION WHEN OTHERS THEN
    -- Fallback view without embedding if columns don't exist
    EXECUTE 'CREATE OR REPLACE VIEW search_stats AS
    SELECT
        (SELECT count(*) FROM items WHERE search_vector IS NOT NULL) AS items_with_search_vector,
        0 AS items_with_embedding,
        (SELECT count(*) FROM items WHERE deleted_at IS NULL) AS total_active_items,
        (SELECT pg_size_pretty(pg_total_relation_size(''items''))) AS items_table_size,
        COALESCE((SELECT pg_size_pretty(pg_relation_size(''idx_items_search_vector''))), ''0 bytes'') AS search_index_size,
        COALESCE((SELECT pg_size_pretty(pg_relation_size(''idx_items_title_trgm''))), ''0 bytes'') AS trgm_title_index_size,
        ''0 bytes'' AS vector_index_size';
END $$;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON FUNCTION fuzzy_search_items IS 'Combined full-text + trigram fuzzy search with typo tolerance';
COMMENT ON FUNCTION search_suggestions IS 'Autocomplete suggestions with fuzzy matching';
COMMENT ON FUNCTION phonetic_search_items IS 'Search by phonetic similarity (soundex/metaphone)';
COMMENT ON FUNCTION typo_distance IS 'Calculate edit distance between two strings (max 3)';
COMMENT ON VIEW search_stats IS 'Search infrastructure statistics';
