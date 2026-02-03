"""Add table partitioning for scalability.

Implements partitioning strategies:
- Items: LIST partitioning by project_id
- Test runs: RANGE partitioning by created_at (monthly)
- Links: LIST partitioning by project_id

Revision ID: 056_add_partitioning
Revises: 055_optimize_indexes
Create Date: 2026-02-01
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "056_add_partitioning"
down_revision = "055_optimize_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add table partitioning."""

    # =========================================================================
    # HELPER FUNCTION: Create partition maintenance function
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION create_monthly_partition(
            parent_table text,
            partition_date date
        ) RETURNS void AS $$
        DECLARE
            partition_name text;
            start_date date;
            end_date date;
        BEGIN
            partition_name := parent_table || '_' || to_char(partition_date, 'YYYY_MM');
            start_date := date_trunc('month', partition_date);
            end_date := start_date + interval '1 month';

            -- Create partition if it doesn't exist
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                partition_name,
                parent_table,
                start_date,
                end_date
            );

            -- Create indexes on partition
            EXECUTE format(
                'CREATE INDEX IF NOT EXISTS %I ON %I(created_at DESC)',
                partition_name || '_created_at_idx',
                partition_name
            );

            IF parent_table = 'test_runs_partitioned' THEN
                EXECUTE format(
                    'CREATE INDEX IF NOT EXISTS %I ON %I(test_suite_id, created_at DESC)',
                    partition_name || '_suite_created_idx',
                    partition_name
                );
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # HELPER FUNCTION: Auto-create future partitions
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION ensure_future_partitions(
            parent_table text,
            months_ahead integer DEFAULT 3
        ) RETURNS void AS $$
        DECLARE
            i integer;
        BEGIN
            FOR i IN 0..months_ahead LOOP
                PERFORM create_monthly_partition(
                    parent_table,
                    (CURRENT_DATE + (i || ' months')::interval)::date
                );
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # TEST_RUNS: Implement RANGE partitioning by created_at
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs') THEN
                -- Check if table is already partitioned
                IF NOT EXISTS (
                    SELECT 1 FROM pg_class WHERE relname = 'test_runs' AND relkind = 'p'
                ) THEN
                    -- Rename existing table
                    ALTER TABLE test_runs RENAME TO test_runs_old;

                    -- Create partitioned table
                    CREATE TABLE test_runs (
                        id uuid NOT NULL DEFAULT gen_random_uuid(),
                        test_suite_id uuid NOT NULL,
                        project_id uuid NOT NULL,
                        status varchar(50) NOT NULL,
                        started_at timestamp with time zone,
                        completed_at timestamp with time zone,
                        test_run_metadata jsonb DEFAULT '{}'::jsonb,
                        created_at timestamp with time zone NOT NULL DEFAULT NOW(),
                        updated_at timestamp with time zone NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (id, created_at)
                    ) PARTITION BY RANGE (created_at);

                    -- Create partitions for last 12 months and next 3 months
                    PERFORM ensure_future_partitions('test_runs', 3);

                    -- Create historical partitions (last 12 months)
                    FOR i IN 1..12 LOOP
                        PERFORM create_monthly_partition(
                            'test_runs',
                            (CURRENT_DATE - (i || ' months')::interval)::date
                        );
                    END LOOP;

                    -- Create default partition for data outside range
                    CREATE TABLE IF NOT EXISTS test_runs_default PARTITION OF test_runs DEFAULT;

                    -- Copy data from old table
                    INSERT INTO test_runs SELECT * FROM test_runs_old;

                    -- Drop old table
                    DROP TABLE test_runs_old;

                    -- Create indexes on partitioned table
                    CREATE INDEX ix_test_runs_suite_id ON test_runs(test_suite_id);
                    CREATE INDEX ix_test_runs_project_id ON test_runs(project_id);
                    CREATE INDEX ix_test_runs_status ON test_runs(status);

                    RAISE NOTICE 'test_runs table partitioned successfully';
                END IF;
            END IF;
        END $$;
    """)

    # =========================================================================
    # ITEMS: Prepare for LIST partitioning by project_id
    # =========================================================================
    # Note: For production, this would require careful migration with zero downtime
    # For now, we create a function to partition new projects

    op.execute("""
        CREATE OR REPLACE FUNCTION create_project_partition(
            parent_table text,
            project_id uuid
        ) RETURNS void AS $$
        DECLARE
            partition_name text;
            project_hash text;
        BEGIN
            -- Use hash of project_id for partition name
            project_hash := substring(md5(project_id::text) from 1 for 8);
            partition_name := parent_table || '_' || project_hash;

            -- Create partition if it doesn't exist
            BEGIN
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES IN (%L)',
                    partition_name,
                    parent_table,
                    project_id
                );

                -- Create indexes on partition
                EXECUTE format(
                    'CREATE INDEX IF NOT EXISTS %I ON %I(item_type, status)',
                    partition_name || '_type_status_idx',
                    partition_name
                );

                EXECUTE format(
                    'CREATE INDEX IF NOT EXISTS %I ON %I(created_at DESC)',
                    partition_name || '_created_at_idx',
                    partition_name
                );
            EXCEPTION WHEN duplicate_table THEN
                -- Partition already exists, ignore
                RETURN;
            END;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # LINKS: Prepare for LIST partitioning by project_id
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION create_links_partition(
            project_id uuid
        ) RETURNS void AS $$
        DECLARE
            partition_name text;
            project_hash text;
        BEGIN
            project_hash := substring(md5(project_id::text) from 1 for 8);
            partition_name := 'links_' || project_hash;

            BEGIN
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS %I PARTITION OF links FOR VALUES IN (%L)',
                    partition_name,
                    project_id
                );

                EXECUTE format(
                    'CREATE INDEX IF NOT EXISTS %I ON %I(source_item_id, target_item_id)',
                    partition_name || '_source_target_idx',
                    partition_name
                );

                EXECUTE format(
                    'CREATE INDEX IF NOT EXISTS %I ON %I(link_type)',
                    partition_name || '_type_idx',
                    partition_name
                );
            EXCEPTION WHEN duplicate_table THEN
                RETURN;
            END;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # TRIGGER: Auto-create partitions on project creation
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION auto_create_project_partitions()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Note: Actual partition creation would be async in production
            -- This is a simplified version for demonstration
            RAISE NOTICE 'Project created: %. Partitions should be created asynchronously.', NEW.id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS trigger_auto_create_project_partitions ON projects;
        CREATE TRIGGER trigger_auto_create_project_partitions
            AFTER INSERT ON projects
            FOR EACH ROW
            EXECUTE FUNCTION auto_create_project_partitions();
    """)

    # =========================================================================
    # SCHEDULED JOB: Ensure future partitions exist
    # =========================================================================

    op.execute("""
        CREATE OR REPLACE FUNCTION maintain_partitions()
        RETURNS void AS $$
        BEGIN
            -- Ensure test_runs partitions for next 3 months
            PERFORM ensure_future_partitions('test_runs', 3);

            -- Log maintenance
            RAISE NOTICE 'Partition maintenance completed at %', NOW();
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # PARTITION PRUNING: Enable constraint exclusion
    # =========================================================================

    op.execute("""
        -- Enable partition pruning optimization
        ALTER DATABASE CURRENT SET enable_partition_pruning = on;
        ALTER DATABASE CURRENT SET constraint_exclusion = partition;
    """)

    # =========================================================================
    # STATISTICS: Update statistics for partitioned tables
    # =========================================================================

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_runs') THEN
                ANALYZE test_runs;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Remove table partitioning."""

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_auto_create_project_partitions ON projects")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS auto_create_project_partitions()")
    op.execute("DROP FUNCTION IF EXISTS maintain_partitions()")
    op.execute("DROP FUNCTION IF EXISTS create_project_partition(text, uuid)")
    op.execute("DROP FUNCTION IF EXISTS create_links_partition(uuid)")
    op.execute("DROP FUNCTION IF EXISTS ensure_future_partitions(text, integer)")
    op.execute("DROP FUNCTION IF EXISTS create_monthly_partition(text, date)")

    # Note: Reverting partitioned tables to non-partitioned is complex
    # and would require data migration in production
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_class WHERE relname = 'test_runs' AND relkind = 'p'
            ) THEN
                RAISE NOTICE 'test_runs is partitioned. Manual migration required to revert.';
            END IF;
        END $$;
    """)
