-- Add updated_at column to links table to match the Link model
ALTER TABLE links
ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to have updated_at equal to created_at
UPDATE links SET updated_at = created_at WHERE updated_at = CURRENT_TIMESTAMP;
