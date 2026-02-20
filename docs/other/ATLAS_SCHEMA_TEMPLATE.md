# Atlas Schema Template for TraceRTM

## Complete schema.hcl for TraceRTM

```hcl
# Atlas Schema Definition for TraceRTM

variable "db_url" {
  type = string
}

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
  index "idx_workos_id" {
    columns = [column.workos_id]
    unique = true
  }
  index "idx_email" {
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
  foreign_key "fk_profile" {
    columns = [column.profile_id]
    ref_columns = [table.profiles.column.id]
    on_delete = CASCADE
  }
  index "idx_profile_id" {
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
  column "status" {
    null = false
    type = varchar(50)
    default = "'open'"
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
  foreign_key "fk_project" {
    columns = [column.project_id]
    ref_columns = [table.projects.column.id]
    on_delete = CASCADE
  }
  index "idx_project_id" {
    columns = [column.project_id]
  }
  index "idx_status" {
    columns = [column.status]
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
  foreign_key "fk_source" {
    columns = [column.source_id]
    ref_columns = [table.items.column.id]
    on_delete = CASCADE
  }
  foreign_key "fk_target" {
    columns = [column.target_id]
    ref_columns = [table.items.column.id]
    on_delete = CASCADE
  }
  index "idx_source_id" {
    columns = [column.source_id]
  }
  index "idx_target_id" {
    columns = [column.target_id]
  }
  index "idx_link_type" {
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
  foreign_key "fk_project" {
    columns = [column.project_id]
    ref_columns = [table.projects.column.id]
    on_delete = CASCADE
  }
  index "idx_project_id" {
    columns = [column.project_id]
  }
  index "idx_status" {
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
  index "idx_entity" {
    columns = [column.entity_type, column.entity_id]
  }
  index "idx_created_at" {
    columns = [column.created_at]
  }
}
```

## How to Use This Template

1. Save as `backend/schema.hcl`
2. Customize table names and columns as needed
3. Add any additional tables
4. Run `atlas migrate diff --env local --name init`
5. Review generated migration
6. Apply with `atlas migrate apply --env local`

## Key Features

- ✅ UUID primary keys
- ✅ Timestamps (created_at, updated_at)
- ✅ Foreign keys with CASCADE delete
- ✅ JSONB metadata columns
- ✅ Proper indexes
- ✅ Status enums
- ✅ WorkOS integration (workos_id)

## Next Steps

1. Create `backend/schema.hcl` with this content
2. Create `backend/atlas.hcl` configuration
3. Generate first migration
4. Test locally
5. Integrate with main.go
6. Deploy to Supabase

