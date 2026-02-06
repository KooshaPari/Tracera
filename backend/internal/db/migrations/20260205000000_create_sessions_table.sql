-- Create sessions table for OAuth/authentication sessions
CREATE TABLE IF NOT EXISTS sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  provider varchar(50) NOT NULL DEFAULT 'claude',
  access_token_encrypted bytea NOT NULL,
  refresh_token_encrypted bytea,
  token_type varchar(50) DEFAULT 'Bearer',
  expires_at timestamp NOT NULL,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  revoked_at timestamp,
  PRIMARY KEY (id),
  UNIQUE (user_id, provider)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_provider ON sessions(provider);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_revoked_at ON sessions(revoked_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user_provider ON sessions(user_id, provider);

-- Create oauth_tokens table for storing encrypted tokens separately
-- This adds an extra layer of security by separating token storage from session metadata
CREATE TABLE IF NOT EXISTS oauth_tokens (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL,
  provider varchar(50) NOT NULL,
  access_token_encrypted bytea NOT NULL,
  refresh_token_encrypted bytea,
  token_expires_at timestamp,
  scope varchar(1000),
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY (id),
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
  UNIQUE (session_id)
);

CREATE INDEX IF NOT EXISTS idx_oauth_tokens_session_id ON oauth_tokens(session_id);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_provider ON oauth_tokens(provider);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_token_expires_at ON oauth_tokens(token_expires_at);
