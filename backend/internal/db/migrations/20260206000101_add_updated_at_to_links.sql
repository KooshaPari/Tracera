-- Add updated_at column to links table to match the Link model (idempotent)
ALTER TABLE links
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to have updated_at equal to created_at (only if column was just added)
UPDATE links
SET updated_at = created_at
WHERE updated_at IS NULL OR updated_at = CURRENT_TIMESTAMP;
