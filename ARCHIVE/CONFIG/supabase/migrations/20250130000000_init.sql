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

CREATE INDEX idx_workos_id ON profiles(workos_id);
CREATE INDEX idx_email ON profiles(email);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  name varchar(255) NOT NULL,
  description text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_profile_id ON projects(profile_id);

-- Create items table
CREATE TABLE IF NOT EXISTS items (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  title varchar(255) NOT NULL,
  description text,
  status varchar(50) NOT NULL DEFAULT 'open',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_items_status ON items(status);

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

CREATE INDEX idx_links_source_id ON links(source_id);
CREATE INDEX idx_links_target_id ON links(target_id);
CREATE INDEX idx_links_link_type ON links(link_type);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  name varchar(255) NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'idle',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_agents_project_id ON agents(project_id);
CREATE INDEX idx_agents_status ON agents(status);

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

CREATE INDEX idx_change_log_entity ON change_log(entity_type, entity_id);
CREATE INDEX idx_change_log_created_at ON change_log(created_at);

-- Create events table (for event sourcing)
CREATE TABLE IF NOT EXISTS events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
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

CREATE INDEX idx_events_entity_id ON events(entity_id);
CREATE INDEX idx_events_project_id ON events(project_id);
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_entity_version ON events(entity_id, version);
CREATE INDEX idx_events_correlation_id ON events(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_events_causation_id ON events(causation_id) WHERE causation_id IS NOT NULL;

-- Create snapshots table (for event sourcing optimization)
CREATE TABLE IF NOT EXISTS snapshots (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  entity_type varchar(50) NOT NULL,
  entity_id uuid NOT NULL,
  version integer NOT NULL,
  state jsonb NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  UNIQUE (entity_id, version)
);

CREATE INDEX idx_snapshots_entity_id ON snapshots(entity_id);
CREATE INDEX idx_snapshots_project_id ON snapshots(project_id);
CREATE INDEX idx_snapshots_entity_version ON snapshots(entity_id, version);

