-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  workos_id varchar(255) NOT NULL,
  email varchar(255) NOT NULL,
  name varchar(255),
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (workos_id),
  UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_workos_id ON profiles(workos_id);
CREATE INDEX IF NOT EXISTS idx_email ON profiles(email);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid,
  name varchar(255) NOT NULL,
  description text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  deleted_at timestamp,
  PRIMARY KEY (id)
);

-- Add missing columns to projects table if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'profile_id'
  ) THEN
    ALTER TABLE projects ADD COLUMN profile_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'name'
  ) THEN
    ALTER TABLE projects ADD COLUMN name varchar(255) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'description'
  ) THEN
    ALTER TABLE projects ADD COLUMN description text;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'metadata'
  ) THEN
    ALTER TABLE projects ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE projects ADD COLUMN created_at timestamp NOT NULL DEFAULT now();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'updated_at'
  ) THEN
    ALTER TABLE projects ADD COLUMN updated_at timestamp NOT NULL DEFAULT now();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'projects' AND column_name = 'deleted_at'
  ) THEN
    ALTER TABLE projects ADD COLUMN deleted_at timestamp;
  END IF;
END
$$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name = 'projects' AND constraint_name = 'projects_profile_id_fkey'
  ) THEN
    ALTER TABLE projects ADD CONSTRAINT projects_profile_id_fkey
      FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_projects_profile_id ON projects(profile_id);

-- Create items table
CREATE TABLE IF NOT EXISTS items (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid,
  title varchar(255) NOT NULL,
  description text,
  status varchar(50) NOT NULL DEFAULT 'open',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id)
);

-- Add missing columns to items table if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'project_id'
  ) THEN
    ALTER TABLE items ADD COLUMN project_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'title'
  ) THEN
    ALTER TABLE items ADD COLUMN title varchar(255) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'description'
  ) THEN
    ALTER TABLE items ADD COLUMN description text;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'status'
  ) THEN
    ALTER TABLE items ADD COLUMN status varchar(50) NOT NULL DEFAULT 'open';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'metadata'
  ) THEN
    ALTER TABLE items ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE items ADD COLUMN created_at timestamp NOT NULL DEFAULT now();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'items' AND column_name = 'updated_at'
  ) THEN
    ALTER TABLE items ADD COLUMN updated_at timestamp NOT NULL DEFAULT now();
  END IF;
END
$$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name = 'items' AND constraint_name = 'items_project_id_fkey'
  ) THEN
    ALTER TABLE items ADD CONSTRAINT items_project_id_fkey
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_items_project_id ON items(project_id);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);

-- Create links table
CREATE TABLE IF NOT EXISTS links (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_id uuid NOT NULL,
  target_id uuid NOT NULL,
  link_type varchar(100) NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (source_id) REFERENCES items(id) ON DELETE CASCADE,
  FOREIGN KEY (target_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_source_id ON links(source_id);
CREATE INDEX IF NOT EXISTS idx_links_target_id ON links(target_id);
CREATE INDEX IF NOT EXISTS idx_links_link_type ON links(link_type);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid,
  name varchar(255) NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'idle',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id)
);

-- Add missing columns to agents table if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'project_id'
  ) THEN
    ALTER TABLE agents ADD COLUMN project_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'name'
  ) THEN
    ALTER TABLE agents ADD COLUMN name varchar(255) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'status'
  ) THEN
    ALTER TABLE agents ADD COLUMN status varchar(50) NOT NULL DEFAULT 'idle';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'metadata'
  ) THEN
    ALTER TABLE agents ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE agents ADD COLUMN created_at timestamp NOT NULL DEFAULT now();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'agents' AND column_name = 'updated_at'
  ) THEN
    ALTER TABLE agents ADD COLUMN updated_at timestamp NOT NULL DEFAULT now();
  END IF;
END
$$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name = 'agents' AND constraint_name = 'agents_project_id_fkey'
  ) THEN
    ALTER TABLE agents ADD CONSTRAINT agents_project_id_fkey
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_agents_project_id ON agents(project_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- Create change_log table
CREATE TABLE IF NOT EXISTS change_log (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  entity_type varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  action varchar(50) NOT NULL,
  changes jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_change_log_entity ON change_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_change_log_created_at ON change_log(created_at);

-- Create events table (for event sourcing)
CREATE TABLE IF NOT EXISTS events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid,
  entity_type varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  event_type varchar(100) NOT NULL,
  data jsonb NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  version integer NOT NULL DEFAULT 1,
  causation_id uuid,
  correlation_id uuid,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id)
);

-- Add missing columns to events table if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'project_id'
  ) THEN
    ALTER TABLE events ADD COLUMN project_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'entity_type'
  ) THEN
    ALTER TABLE events ADD COLUMN entity_type varchar(50) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'entity_id'
  ) THEN
    ALTER TABLE events ADD COLUMN entity_id uuid NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'event_type'
  ) THEN
    ALTER TABLE events ADD COLUMN event_type varchar(100) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'data'
  ) THEN
    ALTER TABLE events ADD COLUMN data jsonb NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'metadata'
  ) THEN
    ALTER TABLE events ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'version'
  ) THEN
    ALTER TABLE events ADD COLUMN version integer NOT NULL DEFAULT 1;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'causation_id'
  ) THEN
    ALTER TABLE events ADD COLUMN causation_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'correlation_id'
  ) THEN
    ALTER TABLE events ADD COLUMN correlation_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'events' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE events ADD COLUMN created_at timestamp NOT NULL DEFAULT now();
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_events_entity_id ON events(entity_id);
CREATE INDEX IF NOT EXISTS idx_events_project_id ON events(project_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_events_entity_version ON events(entity_id, version);
CREATE INDEX IF NOT EXISTS idx_events_correlation_id ON events(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_causation_id ON events(causation_id) WHERE causation_id IS NOT NULL;

-- Create snapshots table (for event sourcing optimization)
CREATE TABLE IF NOT EXISTS snapshots (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid,
  entity_type varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  version integer NOT NULL,
  state jsonb NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (entity_id, version)
);

-- Add missing columns to snapshots table if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'project_id'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN project_id uuid;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'entity_type'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN entity_type varchar(50) NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'entity_id'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN entity_id uuid NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'version'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN version integer NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'state'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN state jsonb NOT NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'snapshots' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE snapshots ADD COLUMN created_at timestamp NOT NULL DEFAULT now();
  END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_snapshots_entity_id ON snapshots(entity_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_project_id ON snapshots(project_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_entity_version ON snapshots(entity_id, version);

