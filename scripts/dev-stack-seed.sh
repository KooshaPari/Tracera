#!/usr/bin/env bash
set -euo pipefail

compose() { docker compose -f docker-compose.dev.yml "$@"; }
wait_for() { compose ps --status running --services | grep -Fxq "$1" || sleep 2; }
for service in kafka-zookeeper clickhouse meilisearch qdrant neo4j5; do
  wait_for "$service"
done

compose exec -T kafka-zookeeper kafka-topics.sh --bootstrap-server kafka-zookeeper:9092 \
  --create --if-not-exists --topic tracera.events --partitions 3 --replication-factor 1
compose exec -T kafka-zookeeper kafka-topics.sh --bootstrap-server kafka-zookeeper:9092 \
  --create --if-not-exists --topic tracera.audit --partitions 1 --replication-factor 1

compose exec -T meilisearch curl -fsS -X POST \
  -H 'Authorization: Bearer tracera_meili_dev' \
  -H 'Content-Type: application/json' \
  http://localhost:7700/indexes -d '{"uid":"tracera_entities","primaryKey":"id"}'
compose exec -T meilisearch curl -fsS -X POST \
  -H 'Authorization: Bearer tracera_meili_dev' \
  -H 'Content-Type: application/json' \
  http://localhost:7700/indexes -d '{"uid":"tracera_documents","primaryKey":"id"}'

compose exec -T qdrant curl -fsS -X PUT http://localhost:6333/collections/tracera_embeddings \
  -H 'Content-Type: application/json' -d '{"vectors":{"size":384,"distance":"Cosine"}}'
compose exec -T qdrant curl -fsS -X PUT http://localhost:6333/collections/tracera_entities \
  -H 'Content-Type: application/json' -d '{"vectors":{"size":384,"distance":"Cosine"}}'

compose exec -T clickhouse clickhouse-client --multiquery <<'SQL'
CREATE DATABASE IF NOT EXISTS tracera;
CREATE TABLE IF NOT EXISTS tracera.events (event_id UUID, entity_id String, event_type String, occurred_at DateTime64(3), payload String) ENGINE = MergeTree ORDER BY (event_type, occurred_at);
CREATE TABLE IF NOT EXISTS tracera.audit_log (id UInt64, actor String, action String, created_at DateTime DEFAULT now()) ENGINE = MergeTree ORDER BY (action, created_at);
SQL

compose exec -T neo4j5 cypher-shell -u neo4j -p tracera_dev --format plain <<'CYPHER'
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;
CREATE INDEX entity_type IF NOT EXISTS FOR (n:Entity) ON (n.type);
CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name);
CYPHER

printf 'Tracera development stack seeded successfully.\n'
