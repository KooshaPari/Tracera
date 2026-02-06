# Atlas Schema Definition for TraceRTM
# Note: Extensions (pg_trgm, fuzzystrmatch, unaccent, vector) are managed via SQL migration

# Profiles Table (WorkOS Users)
table "profiles" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "workos_id" {
    null = false
    type = varchar(255)
  }
  column "email" {
    null = false
    type = varchar(255)
  }
  column "name" {
    type = varchar(255)
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  index "idx_profiles_workos_id" {
    columns = [column.workos_id]
    unique = true
  }
  index "idx_profiles_email" {
    columns = [column.email]
    unique = true
  }
}

# Projects Table
table "projects" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "profile_id" {
    null = false
    type = uuid
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "description" {
    type = text
  }
  column "metadata" {
    type = jsonb
    default = sql("'{}'::jsonb")
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_projects_profile" {
    columns = [column.profile_id]
    ref_columns = [table.profiles.column.id]
    on_delete = CASCADE
  }
  index "idx_projects_profile_id" {
    columns = [column.profile_id]
  }
}

# Items Table
table "items" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "project_id" {
    null = false
    type = uuid
  }
  column "title" {
    null = false
    type = varchar(255)
  }
  column "description" {
    type = text
  }
  column "type" {
    null = false
    type = varchar(50)
    default = "'requirement'"
  }
  column "status" {
    null = false
    type = varchar(50)
    default = "'open'"
  }
  column "priority" {
    type = integer
    default = 0
  }
  column "metadata" {
    type = jsonb
    default = sql("'{}'::jsonb")
  }
  # Full-text search vector (auto-populated by trigger)
  column "search_vector" {
    type = sql("tsvector")
  }
  # AI embeddings for semantic search (voyage-3.5 = 1024 dimensions)
  column "embedding" {
    type = sql("vector(1024)")
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  column "deleted_at" {
    type = timestamp
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_items_project" {
    columns = [column.project_id]
    ref_columns = [table.projects.column.id]
    on_delete = CASCADE
  }
  index "idx_items_project_id" {
    columns = [column.project_id]
  }
  index "idx_items_status" {
    columns = [column.status]
  }
  index "idx_items_type" {
    columns = [column.type]
  }
}

# Links Table
table "links" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "source_id" {
    null = false
    type = uuid
  }
  column "target_id" {
    null = false
    type = uuid
  }
  column "link_type" {
    null = false
    type = varchar(100)
  }
  column "metadata" {
    type = jsonb
    default = sql("'{}'::jsonb")
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_links_source" {
    columns = [column.source_id]
    ref_columns = [table.items.column.id]
    on_delete = CASCADE
  }
  foreign_key "fk_links_target" {
    columns = [column.target_id]
    ref_columns = [table.items.column.id]
    on_delete = CASCADE
  }
  index "idx_links_source_id" {
    columns = [column.source_id]
  }
  index "idx_links_target_id" {
    columns = [column.target_id]
  }
  index "idx_links_link_type" {
    columns = [column.link_type]
  }
}

# Agents Table
table "agents" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "project_id" {
    null = false
    type = uuid
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "status" {
    null = false
    type = varchar(50)
    default = "'idle'"
  }
  column "metadata" {
    type = jsonb
    default = sql("'{}'::jsonb")
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_agents_project" {
    columns = [column.project_id]
    ref_columns = [table.projects.column.id]
    on_delete = CASCADE
  }
  index "idx_agents_project_id" {
    columns = [column.project_id]
  }
  index "idx_agents_status" {
    columns = [column.status]
  }
}

# Change Log Table
table "change_log" {
  schema = schema.public
  column "id" {
    null = false
    type = uuid
    default = sql("gen_random_uuid()")
  }
  column "entity_type" {
    null = false
    type = varchar(50)
  }
  column "entity_id" {
    null = false
    type = uuid
  }
  column "action" {
    null = false
    type = varchar(50)
  }
  column "changes" {
    type = jsonb
  }
  column "created_at" {
    null = false
    type = timestamp
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  index "idx_change_log_entity" {
    columns = [column.entity_type, column.entity_id]
  }
  index "idx_change_log_created_at" {
    columns = [column.created_at]
  }
}

# =============================================================================
# Schema Definition
# =============================================================================
schema "public" {
}
