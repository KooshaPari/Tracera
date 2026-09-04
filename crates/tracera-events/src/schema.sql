-- Tracera events schema for ClickHouse.
--
-- This file is the canonical definition for the five primary analytics tables:
--
--     agent_runs  – one row per agent execution
--     decisions   – decisions made during an agent run
--     deploys     – deploy events per release
--     traces      – distributed-trace spans (OpenTelemetry-style)
--     llm_calls   – LLM prompts / completions (token counts, latency)
--
-- Apply with:
--
--     clickhouse-client --multiquery < schema.sql
--
-- The schema assumes a database named `tracera` (override at deploy time).
-- All timestamps are stored as DateTime64(9) (nanoseconds) so analytics
-- queries can aggregate at sub-millisecond resolution.

-- ---------------------------------------------------------------------------
-- agent_runs
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.agent_runs (
    run_id        UUID,
    agent         LowCardinality(String),
    environment   LowCardinality(String),
    status        Enum8(
        'Pending'   = 0,
        'Running'   = 1,
        'Succeeded' = 2,
        'Failed'    = 3,
        'Cancelled' = 4
    ),
    started_at    DateTime64(9),
    ended_at      Nullable(DateTime64(9)),
    error_message Nullable(String),
    metadata      String DEFAULT '{}'
) ENGINE = MergeTree
  PARTITION BY toYYYYMM(started_at)
  ORDER BY (agent, environment, started_at, run_id)
  SETTINGS index_granularity = 8192;

-- ---------------------------------------------------------------------------
-- decisions
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.decisions (
    decision_id   UUID,
    run_id        UUID,
    kind          LowCardinality(String),
    rationale     String,
    trace_link_id Nullable(String),
    decided_at    DateTime64(9)
) ENGINE = MergeTree
  PARTITION BY toYYYYMM(decided_at)
  ORDER BY (run_id, decided_at, decision_id)
  SETTINGS index_granularity = 8192;

-- ---------------------------------------------------------------------------
-- deploys
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.deploys (
    deploy_id    UUID,
    component    LowCardinality(String),
    environment  Enum8(
        'local'      = 0,
        'ci'         = 1,
        'staging'    = 2,
        'production' = 3
    ),
    commit_sha   String,
    version      LowCardinality(Nullable(String)),
    deployed_at  DateTime64(9),
    duration_ms  UInt32,
    succeeded    UInt8
) ENGINE = MergeTree
  PARTITION BY toYYYYMM(deployed_at)
  ORDER BY (component, environment, deployed_at, deploy_id)
  SETTINGS index_granularity = 8192;

-- ---------------------------------------------------------------------------
-- traces
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.traces (
    trace_id       FixedString(32),  -- 16 bytes hex-encoded
    span_id        String,            -- 8 bytes hex-encoded
    parent_span_id Nullable(String),
    name           LowCardinality(String),
    service        LowCardinality(String),
    started_at     DateTime64(9),
    duration_ns    UInt64,
    status_code    LowCardinality(String),  -- OK | ERROR | UNSET
    attributes     String DEFAULT '{}'
) ENGINE = MergeTree
  PARTITION BY toYYYYMM(started_at)
  ORDER BY (service, started_at, trace_id, span_id)
  TTL toDateTime(started_at) + INTERVAL 30 DAY
  SETTINGS index_granularity = 8192;

-- ---------------------------------------------------------------------------
-- llm_calls
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.llm_calls (
    call_id           UUID,
    trace_id          Nullable(FixedString(32)),
    provider          LowCardinality(String),
    model             LowCardinality(String),
    prompt_tokens     UInt32,
    completion_tokens UInt32,
    latency_ms        UInt32,
    succeeded         UInt8,
    called_at         DateTime64(9)
) ENGINE = MergeTree
  PARTITION BY toYYYYMM(called_at)
  ORDER BY (provider, model, called_at, call_id)
  SETTINGS index_granularity = 8192;

-- ---------------------------------------------------------------------------
-- Materialised view: roll-up of llm_calls per day / provider / model.
-- Useful for the `analytics::llm_daily` query and as a fast cache for the
-- dashboard.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tracera.llm_calls_daily_mv
(
    day               Date,
    provider             LowCardinality(String),
    model                LowCardinality(String),
    prompt_tokens        UInt64,
    completion_tokens    UInt64,
    total_tokens         UInt64,
    succeeded_calls      UInt64,
    failed_calls         UInt64,
    avg_latency_ms       Float64
) ENGINE = SummingMergeTree
  PARTITION BY toYYYYMM(day)
  ORDER BY (day, provider, model);

CREATE MATERIALIZED VIEW IF NOT EXISTS tracera.llm_calls_daily
TO tracera.llm_calls_daily_mv AS
SELECT toDate(called_at)              AS day,
       provider,
       model,
       sum(prompt_tokens)             AS prompt_tokens,
       sum(completion_tokens)         AS completion_tokens,
       sum(prompt_tokens) + sum(completion_tokens) AS total_tokens,
       countIf(succeeded = 1)         AS succeeded_calls,
       countIf(succeeded = 0)         AS failed_calls,
       avg(latency_ms)                AS avg_latency_ms
  FROM tracera.llm_calls
 GROUP BY day, provider, model;