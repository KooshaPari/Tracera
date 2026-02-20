# Atlas Configuration for TraceRTM

# Local Development Environment
env "local" {
  # Schema source
  src = "file://schema.hcl"

  # Development database (Docker for diffing - will use local PG as target)
  dev = "docker://postgres/15/dev?search_path=public"

  # Local database URL
  url = "postgresql://postgres:postgres@localhost:5432/tracertm_dev"

  # Migration configuration
  migration {
    dir = "file://internal/db/migrations"
  }
}

# Local without Docker (uses URL directly)
env "local_direct" {
  src = "file://schema.hcl"
  url = "postgresql://postgres:postgres@localhost:5432/tracertm_dev?sslmode=disable"

  migration {
    dir = "file://internal/db/migrations"
  }
}

# Staging Environment
env "staging" {
  src = "file://schema.hcl"
  url = getenv("DATABASE_URL_STAGING")

  migration {
    dir = "file://internal/db/migrations"
  }
}

# Production Environment
env "prod" {
  src = "file://schema.hcl"
  url = getenv("DATABASE_URL_PROD")

  migration {
    dir = "file://internal/db/migrations"
  }
}

# Supabase Environment
env "supabase" {
  src = "file://schema.hcl"
  url = getenv("SUPABASE_DATABASE_URL")

  migration {
    dir = "file://internal/db/migrations"
  }
}
