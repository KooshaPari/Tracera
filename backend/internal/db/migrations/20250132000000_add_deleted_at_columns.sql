-- Add deleted_at column to projects table if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'deleted_at'
  ) THEN
    ALTER TABLE projects ADD COLUMN deleted_at timestamp;
  END IF;
END
$$;

-- Add deleted_at column to items table if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'deleted_at'
  ) THEN
    ALTER TABLE items ADD COLUMN deleted_at timestamp;
  END IF;
END
$$;

-- Add deleted_at column to agents table if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'deleted_at'
  ) THEN
    ALTER TABLE agents ADD COLUMN deleted_at timestamp;
  END IF;
END
$$;

-- Add deleted_at column to links table if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'links' AND column_name = 'deleted_at'
  ) THEN
    ALTER TABLE links ADD COLUMN deleted_at timestamp;
  END IF;
END
$$;
