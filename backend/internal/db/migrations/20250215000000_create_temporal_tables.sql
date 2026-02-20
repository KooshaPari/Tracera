-- Create version_branches table for branch management
CREATE TABLE IF NOT EXISTS version_branches (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  name varchar(255) NOT NULL,
  slug varchar(255) NOT NULL,
  description text,
  branch_type varchar(50) NOT NULL DEFAULT 'feature', -- main, release, feature, experiment, hotfix, archive
  parent_branch_id uuid,
  base_version_id uuid,
  status varchar(50) NOT NULL DEFAULT 'active', -- active, review, merged, abandoned, archived
  is_default boolean NOT NULL DEFAULT false,
  is_protected boolean NOT NULL DEFAULT false,
  merged_at timestamp,
  merged_into uuid,
  merged_by varchar(255),
  version_count integer NOT NULL DEFAULT 0,
  item_count integer NOT NULL DEFAULT 0,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_by varchar(255) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (parent_branch_id) REFERENCES version_branches(id) ON DELETE SET NULL,
  UNIQUE (project_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_version_branches_project_id ON version_branches(project_id);
CREATE INDEX IF NOT EXISTS idx_version_branches_status ON version_branches(status);
CREATE INDEX IF NOT EXISTS idx_version_branches_is_default ON version_branches(is_default) WHERE is_default = true;
CREATE INDEX IF NOT EXISTS idx_version_branches_created_at ON version_branches(created_at);

-- Create versions table for version management
CREATE TABLE IF NOT EXISTS versions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  branch_id uuid NOT NULL,
  project_id uuid NOT NULL,
  version_number integer NOT NULL,
  parent_version_id uuid,
  snapshot_id uuid,
  changeset_id uuid,
  tag varchar(255),
  message text NOT NULL,
  item_count integer NOT NULL DEFAULT 0,
  change_count integer NOT NULL DEFAULT 0,
  status varchar(50) NOT NULL DEFAULT 'draft', -- draft, pending_review, approved, rejected, superseded
  approved_by varchar(255),
  approved_at timestamp,
  rejection_reason text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_by varchar(255) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (branch_id) REFERENCES version_branches(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (parent_version_id) REFERENCES versions(id) ON DELETE SET NULL,
  UNIQUE (branch_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_versions_branch_id ON versions(branch_id);
CREATE INDEX IF NOT EXISTS idx_versions_project_id ON versions(project_id);
CREATE INDEX IF NOT EXISTS idx_versions_status ON versions(status);
CREATE INDEX IF NOT EXISTS idx_versions_created_at ON versions(created_at);

-- Create item_versions table for item version snapshots
CREATE TABLE IF NOT EXISTS item_versions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  item_id uuid NOT NULL,
  version_id uuid NOT NULL,
  branch_id uuid NOT NULL,
  project_id uuid NOT NULL,
  state jsonb NOT NULL,
  lifecycle varchar(50),
  introduced_in_version_id uuid,
  last_modified_in_version_id uuid,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  FOREIGN KEY (version_id) REFERENCES versions(id) ON DELETE CASCADE,
  FOREIGN KEY (branch_id) REFERENCES version_branches(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  UNIQUE (item_id, version_id)
);

CREATE INDEX IF NOT EXISTS idx_item_versions_item_id ON item_versions(item_id);
CREATE INDEX IF NOT EXISTS idx_item_versions_version_id ON item_versions(version_id);
CREATE INDEX IF NOT EXISTS idx_item_versions_branch_id ON item_versions(branch_id);
CREATE INDEX IF NOT EXISTS idx_item_versions_created_at ON item_versions(created_at);

-- Create item_alternatives table for alternative items
CREATE TABLE IF NOT EXISTS item_alternatives (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  base_item_id uuid NOT NULL,
  alternative_item_id uuid NOT NULL,
  relationship varchar(100) NOT NULL, -- alternative_to, supersedes, experiment_of
  description text,
  is_chosen boolean NOT NULL DEFAULT false,
  chosen_at timestamp,
  chosen_by varchar(255),
  chosen_reason text,
  metrics jsonb DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (base_item_id) REFERENCES items(id) ON DELETE CASCADE,
  FOREIGN KEY (alternative_item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_item_alternatives_project_id ON item_alternatives(project_id);
CREATE INDEX IF NOT EXISTS idx_item_alternatives_base_item_id ON item_alternatives(base_item_id);
CREATE INDEX IF NOT EXISTS idx_item_alternatives_alternative_item_id ON item_alternatives(alternative_item_id);
CREATE INDEX IF NOT EXISTS idx_item_alternatives_created_at ON item_alternatives(created_at);

-- Create merge_requests table for branch merge operations
CREATE TABLE IF NOT EXISTS merge_requests (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  source_branch_id uuid NOT NULL,
  target_branch_id uuid NOT NULL,
  source_version_id uuid NOT NULL,
  base_version_id uuid,
  status varchar(50) NOT NULL DEFAULT 'open', -- open, approved, merged, closed, conflict
  title varchar(255) NOT NULL,
  description text,
  diff jsonb DEFAULT '{}'::jsonb,
  conflicts jsonb DEFAULT '[]'::jsonb,
  reviewers jsonb DEFAULT '[]'::jsonb,
  approved_by jsonb DEFAULT '[]'::jsonb,
  created_by varchar(255) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  merged_at timestamp,
  merged_by varchar(255),
  closed_at timestamp,
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (source_branch_id) REFERENCES version_branches(id) ON DELETE CASCADE,
  FOREIGN KEY (target_branch_id) REFERENCES version_branches(id) ON DELETE CASCADE,
  FOREIGN KEY (source_version_id) REFERENCES versions(id) ON DELETE CASCADE,
  FOREIGN KEY (base_version_id) REFERENCES versions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_merge_requests_project_id ON merge_requests(project_id);
CREATE INDEX IF NOT EXISTS idx_merge_requests_source_branch_id ON merge_requests(source_branch_id);
CREATE INDEX IF NOT EXISTS idx_merge_requests_target_branch_id ON merge_requests(target_branch_id);
CREATE INDEX IF NOT EXISTS idx_merge_requests_status ON merge_requests(status);
CREATE INDEX IF NOT EXISTS idx_merge_requests_created_at ON merge_requests(created_at);
