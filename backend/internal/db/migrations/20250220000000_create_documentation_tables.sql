-- Create documentation table for storing parsed documentation
CREATE TABLE IF NOT EXISTS documentation (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  title varchar(512) NOT NULL,
  slug varchar(512),
  format varchar(50) NOT NULL, -- markdown, rst, html, plaintext
  content text NOT NULL,
  summary text,
  parsed_structure jsonb DEFAULT '{}', -- stores headings, sections, code blocks
  tags text[] DEFAULT '{}',
  version int DEFAULT 1,
  source_url text, -- if parsed from URL
  file_path text, -- if parsed from file
  full_text_search tsvector, -- for full-text search
  metadata jsonb DEFAULT '{}',
  created_by uuid,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  deleted_at timestamp,
  PRIMARY KEY (id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documentation_project_id ON documentation(project_id);
CREATE INDEX IF NOT EXISTS idx_documentation_slug ON documentation(project_id, slug);
CREATE INDEX IF NOT EXISTS idx_documentation_created_at ON documentation(created_at);
CREATE INDEX IF NOT EXISTS idx_documentation_format ON documentation(format);
CREATE INDEX IF NOT EXISTS idx_documentation_full_text_search ON documentation USING GIN(full_text_search);
CREATE INDEX IF NOT EXISTS idx_documentation_tags ON documentation USING GIN(tags);

-- Create documentation sections table for extracting structure
CREATE TABLE IF NOT EXISTS documentation_sections (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  doc_id uuid NOT NULL,
  level int NOT NULL, -- heading level (1-6 for markdown)
  title varchar(512) NOT NULL,
  content text,
  section_number varchar(50), -- like "1.2.3" for hierarchical structure
  position int, -- position within document
  code_blocks text[],
  links text[], -- links found in this section
  metadata jsonb DEFAULT '{}',
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (doc_id) REFERENCES documentation(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documentation_sections_doc_id ON documentation_sections(doc_id);
CREATE INDEX IF NOT EXISTS idx_documentation_sections_level ON documentation_sections(level);

-- Create documentation links table for tracking relationships
CREATE TABLE IF NOT EXISTS documentation_links (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  source_doc_id uuid NOT NULL,
  target_doc_id uuid, -- NULL if external link
  target_item_id uuid, -- link to items table
  link_type varchar(50), -- references, seeAlso, relatedTo, implements, etc.
  url text, -- external URL if target_doc_id is NULL
  title text,
  description text,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (source_doc_id) REFERENCES documentation(id) ON DELETE CASCADE,
  FOREIGN KEY (target_doc_id) REFERENCES documentation(id) ON DELETE SET NULL,
  FOREIGN KEY (target_item_id) REFERENCES items(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_documentation_links_source ON documentation_links(source_doc_id);
CREATE INDEX IF NOT EXISTS idx_documentation_links_target_doc ON documentation_links(target_doc_id);
CREATE INDEX IF NOT EXISTS idx_documentation_links_target_item ON documentation_links(target_item_id);
CREATE INDEX IF NOT EXISTS idx_documentation_links_type ON documentation_links(link_type);

-- Create documentation search index table for efficient searching
CREATE TABLE IF NOT EXISTS documentation_search_index (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  doc_id uuid NOT NULL,
  doc_title varchar(512),
  section_title varchar(512),
  content_snippet text,
  search_vector tsvector,
  rank float DEFAULT 0.5,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (doc_id) REFERENCES documentation(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documentation_search_index_search ON documentation_search_index USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_documentation_search_index_doc_id ON documentation_search_index(doc_id);

-- Create documentation versions table for version tracking
CREATE TABLE IF NOT EXISTS documentation_versions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  doc_id uuid NOT NULL,
  version_number int NOT NULL,
  content text NOT NULL,
  change_summary text,
  changed_by uuid,
  created_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (doc_id) REFERENCES documentation(id) ON DELETE CASCADE,
  UNIQUE(doc_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_documentation_versions_doc_id ON documentation_versions(doc_id);
CREATE INDEX IF NOT EXISTS idx_documentation_versions_version_number ON documentation_versions(doc_id, version_number DESC);

-- Update trigger for full-text search vector
CREATE OR REPLACE FUNCTION update_documentation_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.full_text_search := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.summary, '') || ' ' || COALESCE(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS documentation_search_vector_trigger ON documentation;
CREATE TRIGGER documentation_search_vector_trigger
BEFORE INSERT OR UPDATE ON documentation
FOR EACH ROW
EXECUTE FUNCTION update_documentation_search_vector();
