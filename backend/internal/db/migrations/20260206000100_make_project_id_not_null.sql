-- Make project_id NOT NULL in items and agents tables
-- This constraint should have been part of the initial schema definition

-- For items table
ALTER TABLE items
ALTER COLUMN project_id SET NOT NULL;

-- For agents table
ALTER TABLE agents
ALTER COLUMN project_id SET NOT NULL;
