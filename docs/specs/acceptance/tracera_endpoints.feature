# Tracera API Endpoint Oracle — Gherkin Acceptance Features
# Status: PENDING (failing targets for migration verification)
# Spec: docs/specs/SPEC.md (FR-1..FR-24)
# Generated: 2026-06-24

Feature: Tracera REST API endpoint oracle
  As a migration verifier
  I want all 24 main endpoints to behave per the oracle spec
  So that capability is preserved across language/runtime migrations

  Background:
    Given the Tracera API is running at "${TRACERA_API_BASE_URL}"
    And a valid Bearer token is available as "${TRACERA_BEARER_TOKEN}"

  # ---------------------------------------------------------------------------
  # auth.py (FR-1)
  # ---------------------------------------------------------------------------

  @FR-1 @auth
  Scenario: FR-1 GET current authenticated user
    Given a valid JWT with claim "sub" equal to "user-001"
    When I send GET "/api/v1/auth/me" with the Bearer token
    Then the response status should be 200
    And the response JSON field "user.id" should equal "user-001"
    And the response JSON should contain key "claims"
    And the response JSON should contain key "account"

  # ---------------------------------------------------------------------------
  # code_trace.py (FR-2)
  # ---------------------------------------------------------------------------

  @FR-2 @code_trace
  Scenario: FR-2 GET UI code trace chain for a component
    Given an item graph exists with root component "${COMPONENT_UUID}" linked to a requirement
    When I send GET "/api/v1/analysis/code-trace/${COMPONENT_UUID}" with the Bearer token
    Then the response status should be 200
    And the response JSON field "id" should equal "${COMPONENT_UUID}"
    And the response JSON array "levels" should not be empty
    And each element in "levels" should have keys "type", "confidence", "strategy"
    And the response JSON field "overallConfidence" should be between 0.0 and 1.0

  # ---------------------------------------------------------------------------
  # comments.py (FR-3..FR-5)
  # ---------------------------------------------------------------------------

  @FR-3 @comments
  Scenario: FR-3 GET list comments for an item
    Given the item_comments table is migrated
    And item "${ITEM_ID}" has at least one comment
    When I send GET "/api/v1/items/${ITEM_ID}/comments" with the Bearer token
    Then the response status should be 200
    And the response should be a JSON array ordered by "created_at" ascending

  @FR-4 @comments
  Scenario: FR-4 POST create a comment on an item
    Given the item_comments table is migrated
    When I send POST "/api/v1/items/${ITEM_ID}/comments" with the Bearer token and body:
      """
      {"content": "oracle acceptance comment"}
      """
    Then the response status should be 201
    And the response JSON field "content" should equal "oracle acceptance comment"
    And the response JSON field "author_id" should equal the token subject

  @FR-5 @comments
  Scenario: FR-5 DELETE own comment on an item
    Given the item_comments table is migrated
    And comment "${COMMENT_ID}" on item "${ITEM_ID}" is owned by the caller
    When I send DELETE "/api/v1/items/${ITEM_ID}/comments/${COMMENT_ID}" with the Bearer token
    Then the response status should be 204
    When I send GET "/api/v1/items/${ITEM_ID}/comments" with the Bearer token
    Then the response JSON array should not contain an element with id "${COMMENT_ID}"

  # ---------------------------------------------------------------------------
  # evidence.py (FR-6..FR-8)
  # ---------------------------------------------------------------------------

  @FR-6 @evidence
  Scenario: FR-6 GET evidence pillar health
    When I send GET "/api/v1/evidence/health"
    Then the response status should be 200
    And the response JSON field "pillar" should equal "evidence"
    And the response JSON field "status" should equal "ok"

  @FR-7 @evidence
  Scenario: FR-7 GET list evidence items
    Given at least one evidence item exists
    When I send GET "/api/v1/evidence"
    Then the response status should be 200
    And each element in the response JSON array should have keys "id", "artifact_id", "kind", "url", "captured_at"

  @FR-8 @evidence
  Scenario: FR-8 POST create evidence item
    When I send POST "/api/v1/evidence" with body:
      """
      {
        "artifact_id": "art-001",
        "kind": "screenshot",
        "url": "https://example.com/evidence.png",
        "captured_at": "2026-06-24T00:00:00Z"
      }
      """
    Then the response status should be 201
    And the response JSON field "artifact_id" should equal "art-001"
    And the response JSON field "kind" should equal "screenshot"
    And the response JSON should contain key "id"

  # ---------------------------------------------------------------------------
  # impact.py (FR-9..FR-10)
  # ---------------------------------------------------------------------------

  @FR-9 @impact
  Scenario: FR-9 GET forward impact from Neo4j graph
    Given artifact "${ARTIFACT_ID}" has downstream trace links in Neo4j
    When I send GET "/api/v1/impact/forward/${ARTIFACT_ID}" with the Bearer token
    Then the response status should be 200
    And the response JSON field "direction" should equal "forward"
    And the response JSON field "artifact_id" should equal "${ARTIFACT_ID}"
    And the response JSON field "total" should equal the length of "affected"

  @FR-10 @impact
  Scenario: FR-10 GET reverse impact from Neo4j graph
    Given artifact "${ARTIFACT_ID}" has upstream trace links in Neo4j
    When I send GET "/api/v1/impact/reverse/${ARTIFACT_ID}" with the Bearer token
    Then the response status should be 200
    And the response JSON field "direction" should equal "reverse"
    And the response JSON field "artifact_id" should equal "${ARTIFACT_ID}"
    And the response JSON field "total" should equal the length of "upstream"

  # ---------------------------------------------------------------------------
  # impact_scoring.py (FR-11)
  # ---------------------------------------------------------------------------

  @FR-11 @impact_scoring
  Scenario: FR-11 POST blast-radius risk scoring
    When I send POST "/api/v1/impact/blast-radius" with the Bearer token and body:
      """
      {
        "artifact_id": "seed-001",
        "artifacts": [
          {"id": "seed-001", "kind": "CODE", "title": "Root"},
          {"id": "child-001", "kind": "REQUIREMENT", "title": "Req"}
        ],
        "links": [
          {"source_artifact_id": "seed-001", "target_artifact_id": "child-001", "confidence": 0.9}
        ],
        "depth": 5
      }
      """
    Then the response status should be 200
    And the response JSON field "artifact_id" should equal "seed-001"
    And the response JSON field "blast_radius_score" should be between 0.0 and 100.0
    And the response JSON field "risk_level" should be one of "LOW", "MEDIUM", "HIGH", "CRITICAL"
    And the response JSON array "affected_artifacts" should not be empty

  # ---------------------------------------------------------------------------
  # ingest.py (FR-12..FR-13)
  # ---------------------------------------------------------------------------

  @FR-12 @ingest
  Scenario: FR-12 POST bulk ingest GitHub issues
    When I send POST "/api/v1/ingest/github" with the Bearer token and body:
      """
      {
        "repo": "KooshaPari/Tracera",
        "issues": [
          {
            "id": 1,
            "number": 1,
            "title": "Oracle issue",
            "body": "Acceptance test body",
            "labels": ["requirement"]
          }
        ]
      }
      """
    Then the response status should be 200
    And the response JSON should contain keys "total_processed", "requirements_created", "trace_links_created", "errors"

  @FR-13 @ingest
  Scenario: FR-13 POST bulk ingest Jira issues
    When I send POST "/api/v1/ingest/jira" with the Bearer token and body:
      """
      {
        "issues": [
          {
            "key": "TRC-1",
            "id": "10001",
            "fields": {
              "summary": "Oracle Jira issue",
              "description": "Acceptance test",
              "issuetype": {"name": "Story"}
            }
          }
        ]
      }
      """
    Then the response status should be 200
    And the response JSON field "total_processed" should be at least 1
    And the response JSON should contain keys "requirements_created", "trace_links_created"

  # ---------------------------------------------------------------------------
  # org_intel.py (FR-14..FR-16)
  # ---------------------------------------------------------------------------

  @FR-14 @org_intel
  Scenario: FR-14 GET org-intel pillar health
    When I send GET "/api/v1/org-intel/health"
    Then the response status should be 200
    And the response JSON field "pillar" should equal "org_intel"
    And the response JSON field "status" should equal "ok"

  @FR-15 @org_intel
  Scenario: FR-15 GET organizational metrics
    When I send GET "/api/v1/org-intel/metrics"
    Then the response status should be 200
    And the response JSON field "total_artifacts" should be an integer
    And the response JSON field "coverage_ratio" should be between 0.0 and 1.0
    And the response JSON field "open_gaps" should be an integer

  @FR-16 @org_intel
  Scenario: FR-16 GET list teams
    When I send GET "/api/v1/org-intel/teams"
    Then the response status should be 200
    And the response JSON array should not be empty
    And each element should have keys "id", "name", "description", "members"

  # ---------------------------------------------------------------------------
  # sdlc_pm.py (FR-17..FR-20)
  # ---------------------------------------------------------------------------

  @FR-17 @sdlc_pm
  Scenario: FR-17 GET sdlc-pm pillar health
    When I send GET "/api/v1/sdlc-pm/health"
    Then the response status should be 200
    And the response JSON field "pillar" should equal "sdlc_pm"
    And the response JSON field "status" should equal "ok"

  @FR-18 @sdlc_pm
  Scenario: FR-18 GET list sprints
    When I send GET "/api/v1/sdlc-pm/sprints"
    Then the response status should be 200
    And each element in the response JSON array should have keys "id", "name", "goal", "start_date", "end_date", "status"

  @FR-19 @sdlc_pm
  Scenario: FR-19 GET list stories
    When I send GET "/api/v1/sdlc-pm/stories"
    Then the response status should be 200
    And each element in the response JSON array should have keys "id", "title", "description", "status"

  @FR-20 @sdlc_pm
  Scenario: FR-20 POST create sprint
    When I send POST "/api/v1/sdlc-pm/sprints" with body:
      """
      {
        "name": "Oracle Sprint 1",
        "goal": "Verify endpoint oracle",
        "start_date": "2026-06-24T00:00:00Z",
        "end_date": "2026-07-08T00:00:00Z"
      }
      """
    Then the response status should be 201
    And the response JSON field "name" should equal "Oracle Sprint 1"
    And the response JSON should contain key "id"

  # ---------------------------------------------------------------------------
  # traceability.py (FR-21..FR-24)
  # ---------------------------------------------------------------------------

  @FR-21 @traceability
  Scenario: FR-21 POST build coverage matrix
    When I send POST "/api/v1/coverage-matrix" with body:
      """
      {
        "links": [
          {
            "source_id": "req-001",
            "target_id": "test-001",
            "relationship": "verifies",
            "confidence": 0.95
          }
        ],
        "stale_after_days": 90
      }
      """
    Then the response status should be 200
    And the response JSON field "link_count" should equal 1
    And the response JSON array "cells" should not be empty
    And each cell should have field "coverage" in "covered", "partial", "missing", "stale", "conflict"

  @FR-22 @traceability
  Scenario: FR-22 POST spec-first governance check
    When I send POST "/api/v1/governance/spec-check" with body:
      """
      {
        "specs": [
          {"spec_id": "SPEC-001", "title": "Oracle spec", "status": "approved"}
        ],
        "traces": [
          {"spec_id": "SPEC-001", "trace_type": "test", "trace_ref": "test_governance.py"}
        ]
      }
      """
    Then the response status should be 200
    And the response JSON field "status" should equal "pass"
    And the response JSON array "violations" should be empty

  @FR-23 @traceability
  Scenario: FR-23 POST in-memory impact analysis
    When I send POST "/api/v1/impact" with body:
      """
      {
        "changed_artifact_ids": ["art-001"],
        "links": [
          {
            "source_id": "art-001",
            "target_id": "art-002",
            "relationship": "implements",
            "confidence": 1.0
          }
        ],
        "max_depth": 10
      }
      """
    Then the response status should be 200
    And the response JSON array "seeds" should contain "art-001"
    And the response JSON array "affected" should contain an element with "artifact_id" "art-001" and "depth" 0

  @FR-24 @traceability
  Scenario: FR-24 POST requirement-artifact confidence scoring
    When I send POST "/api/v1/confidence" with body:
      """
      {
        "requirement_text": "The system shall authenticate users",
        "artifact_text": "authenticate users via OAuth token"
      }
      """
    Then the response status should be 200
    And the response JSON field "confidence" should be between 0.0 and 1.0
    And the response JSON field "rationale" should not be empty
