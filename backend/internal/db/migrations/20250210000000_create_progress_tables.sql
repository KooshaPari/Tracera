-- Create milestones table
CREATE TABLE IF NOT EXISTS milestones (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  parent_id uuid,
  name varchar(255) NOT NULL,
  slug varchar(255) NOT NULL,
  description text,
  objective text,
  start_date timestamp,
  target_date timestamp NOT NULL,
  actual_date timestamp,
  status varchar(50) NOT NULL DEFAULT 'not_started',
  health varchar(20) NOT NULL DEFAULT 'unknown',
  risk_score integer NOT NULL DEFAULT 0,
  risk_factors jsonb DEFAULT '[]'::jsonb,
  owner_id uuid,
  tags jsonb DEFAULT '[]'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  deleted_at timestamp,
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (parent_id) REFERENCES milestones(id) ON DELETE SET NULL,
  FOREIGN KEY (owner_id) REFERENCES profiles(id) ON DELETE SET NULL,
  CONSTRAINT valid_status CHECK (status IN ('not_started', 'in_progress', 'at_risk', 'blocked', 'completed', 'cancelled')),
  CONSTRAINT valid_health CHECK (health IN ('green', 'yellow', 'red', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_milestones_project_id ON milestones(project_id);
CREATE INDEX IF NOT EXISTS idx_milestones_parent_id ON milestones(parent_id);
CREATE INDEX IF NOT EXISTS idx_milestones_owner_id ON milestones(owner_id);
CREATE INDEX IF NOT EXISTS idx_milestones_status ON milestones(status);
CREATE INDEX IF NOT EXISTS idx_milestones_target_date ON milestones(target_date);
CREATE INDEX IF NOT EXISTS idx_milestones_slug ON milestones(project_id, slug);

-- Create milestone_items join table
CREATE TABLE IF NOT EXISTS milestone_items (
  milestone_id uuid NOT NULL,
  item_id uuid NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (milestone_id, item_id),
  FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_milestone_items_item_id ON milestone_items(item_id);

-- Create sprints table
CREATE TABLE IF NOT EXISTS sprints (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  name varchar(255) NOT NULL,
  slug varchar(255) NOT NULL,
  goal text,
  start_date timestamp NOT NULL,
  end_date timestamp NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'planning',
  health varchar(20) NOT NULL DEFAULT 'unknown',
  planned_capacity integer,
  actual_capacity integer,
  planned_points integer NOT NULL DEFAULT 0,
  completed_points integer NOT NULL DEFAULT 0,
  remaining_points integer NOT NULL DEFAULT 0,
  added_points integer NOT NULL DEFAULT 0,
  removed_points integer NOT NULL DEFAULT 0,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  completed_at timestamp,
  deleted_at timestamp,
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT valid_sprint_status CHECK (status IN ('planning', 'active', 'completed', 'cancelled')),
  CONSTRAINT valid_sprint_health CHECK (health IN ('green', 'yellow', 'red', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_sprints_project_id ON sprints(project_id);
CREATE INDEX IF NOT EXISTS idx_sprints_status ON sprints(status);
CREATE INDEX IF NOT EXISTS idx_sprints_start_date ON sprints(start_date);
CREATE INDEX IF NOT EXISTS idx_sprints_slug ON sprints(project_id, slug);

-- Create sprint_items join table
CREATE TABLE IF NOT EXISTS sprint_items (
  sprint_id uuid NOT NULL,
  item_id uuid NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (sprint_id, item_id),
  FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sprint_items_item_id ON sprint_items(item_id);

-- Create burndown_data table
CREATE TABLE IF NOT EXISTS burndown_data (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  sprint_id uuid NOT NULL,
  recorded_date timestamp NOT NULL,
  remaining_points integer NOT NULL,
  ideal_points integer NOT NULL,
  completed_points integer NOT NULL,
  added_points integer DEFAULT 0,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_burndown_data_sprint_id ON burndown_data(sprint_id);
CREATE INDEX IF NOT EXISTS idx_burndown_data_date ON burndown_data(sprint_id, recorded_date);

-- Create progress_snapshots table
CREATE TABLE IF NOT EXISTS progress_snapshots (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  snapshot_date timestamp NOT NULL,
  metrics jsonb NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_progress_snapshots_project_id ON progress_snapshots(project_id);
CREATE INDEX IF NOT EXISTS idx_progress_snapshots_date ON progress_snapshots(project_id, snapshot_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_progress_snapshots_unique ON progress_snapshots(project_id, snapshot_date);

-- Create velocity_history table
CREATE TABLE IF NOT EXISTS velocity_history (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  period_start timestamp NOT NULL,
  period_end timestamp NOT NULL,
  period_label varchar(255) NOT NULL,
  planned_points integer NOT NULL,
  completed_points integer NOT NULL,
  velocity integer NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_velocity_history_project_id ON velocity_history(project_id);
CREATE INDEX IF NOT EXISTS idx_velocity_history_period ON velocity_history(project_id, period_start);

-- Create milestone_dependencies table
CREATE TABLE IF NOT EXISTS milestone_dependencies (
  dependent_id uuid NOT NULL,
  dependency_id uuid NOT NULL,
  relationship_type varchar(50) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (dependent_id, dependency_id),
  FOREIGN KEY (dependent_id) REFERENCES milestones(id) ON DELETE CASCADE,
  FOREIGN KEY (dependency_id) REFERENCES milestones(id) ON DELETE CASCADE,
  CONSTRAINT relationship_check CHECK (relationship_type IN ('depends_on', 'blocks'))
);

CREATE INDEX IF NOT EXISTS idx_milestone_dependencies_dependency_id ON milestone_dependencies(dependency_id);
