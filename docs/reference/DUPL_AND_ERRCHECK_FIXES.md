# Dupl and errcheck fixes (backend)

Apply in the **backend** repo. See `REVIVE_FIX_REFERENCE.md` for pattern details.

## dupl – Extract shared logic

| Location | Action |
|----------|--------|
| **equivalence/export** (json_exporter, yaml_exporter, service.go) | Add `calculateStatistics(concepts, projections, links) ExportStatistics` in `service.go` (or a small `stats.go`). Have JSON exporter, YAML exporter, and service call it; remove the three duplicated blocks. |
| **equivalence/import/service.go** (ImportJSON vs ImportYAML) | Extract common flow into e.g. `importFromReader(ctx, projectID, r, opts, parseFn)` where `parseFn` is JSON or YAML parser. Keep only validator/resolver setup, parse, validate, and `applyImport` in the helper. |
| **equivalence/repository.go** (concept scan loop ×2, projection scan ×2) | Add `scanCanonicalConcept(rows)` and `scanCanonicalProjection(rows)` helpers; use in both list-by-project and list-by-parent (and by-item / by-concept for projections). |
| **figma/client.go** (GetComponents vs GetComponentSets) | Extract `getFileSubpath(ctx, fileKey, subpath string) (map[string]interface{}, error)` that builds URL, calls makeRequest, checks StatusOK, decodes JSON. Call it with `"components"` and `"component_sets"`. |
| **handlers/auth_handler.go** (createSessionToken vs extendSession) | Extract e.g. `writeSessionAndSignJWT(ctx, user, ttl) (string, error)` that builds SessionData, marshals, sets Redis, builds JWT, signs. Both create and extend call it. |
| **handlers/temporal_handler.go** (ApproveVersion, RestoreItemVersion, MergeBranches) | Extract a helper e.g. `handleTemporalAction(c, paramName, bodyField, errMsg, svcCall)` that checks nil service, reads param, binds body, validates required field, calls service, returns JSON. |
| **journey/handler.go** (ListJourneys vs ListProjectJourneys) | Extract `listJourneysWithFilter(c, projectID string) error` that parses limit/offset/min_score/type, builds filter, calls repo.List+Count, returns ListJourneysResponse. Both handlers get projectID from query vs path and call it. |
| **progress/handler.go** (CreateMilestone vs CreateSprint) | Extract `createProjectScopedResource(w, r, parseReq, createFn)` that decodes body, parses project_id from query, calls createFn(ctx, projID, req), writes 201 + JSON. |
| **repository/progress_repository.go** (GetMilestonesByProject vs GetMilestonesByParent, GetSprintByID vs GetActiveSprint) | For milestones: one query builder or shared scan loop with different WHERE clause. For sprints: shared scan logic with different query (by id vs by project_id+status+limit 1). |
| **nats/nats.go vs nats/publisher.go** | Extract shared auth option building (file vs JWT+nkey) into internal helper; both `NewNATSClientWithAuth` and `NewEventPublisherWithAuth` use it, then call their respective Connect. |
| **services/codeindex_service_impl.go** (GetCodeEntitiesByType vs GetCodeEntitiesByFile) | Extract `getCodeEntitiesWithCache(ctx, cacheKey, fetchFn) ([]*models.CodeEntity, error)` and a small async cache-set; both methods build their key and pass the right repo method as fetchFn. |
| **Graph/journey/traceability/handler tests** | Prefer table-driven tests or shared helpers (e.g. `runListProjectsTest(t, limit, offset, wantLen)`) instead of duplicate test functions. |
| **internal/services/mocks.go vs services.go** | Mock structs mirroring interfaces is expected; dupl here is structural. Optionally leave as-is or add a single file that defines interface and a codegen/comment that mocks implement it. |

## errcheck – Check or explicitly ignore

| Category | Fix |
|----------|-----|
| **defer conn.Close / resp.Body.Close / cache.Close / encoder.Close** | Use `defer func() { _ = x.Close() }()` (or `Close(ctx)` for pgx). For HTTP body: `defer func() { _ = resp.Body.Close() }()`. |
| **cmd/migrate** `defer conn.Close(ctx)` | `defer func() { _ = conn.Close(ctx) }()`. |
| **json.NewEncoder(w).Encode(...)** in tests/servers | `_ = json.NewEncoder(w).Encode(...)` or `require.NoError(t, json.NewEncoder(w).Encode(...))`. |
| **cache.Set / cache.Get / cache.Delete / cache.InvalidatePattern** in tests | Either `require.NoError(t, cache.Set(...))` or `_ = cache.Set(...)` with comment. Same for Get/Delete/InvalidatePattern. |
| **ReleaseLock / saveTask / store.Store / repo.SaveX** | In production code: check and handle (log or return). In tests: `require.NoError(t, ...)` or `_ = ...` with comment. |
| **fmt.Sscanf / ast.Walk** | Check return value and handle error or document with `_ =` and comment. |
| **w.Write / fmt.Fprint in test handlers** | `_, _ = w.Write(...)` or `_, _ = fmt.Fprint(w, ...)` so errcheck is satisfied. |
| **DropTable / Migrator** in test cleanup | `defer func() { _ = db.Migrator().DropTable(...) }()` or run and ignore only in cleanup. |
| **session.Close(ctx) / driver.Close** (Neo4j) | `defer func() { _ = session.Close(ctx) }()` and same for driver where applicable. |

Use project stance: **require** dependencies and **fail clearly**; for best-effort cleanup (e.g. defer close in tests), explicit `_ =` with a one-line comment is acceptable.
