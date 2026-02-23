# Patent Board TODO Snapshot

## Completed in this cycle

- [x] AnalysisWorkbench API path migration to new MCP routes
- [x] AnalysisWorkbench unit test expectation alignment
- [x] Playwright E2E port stabilization (`3301`, `strictPort`)
- [x] Vite proxy target split for local vs docker (`VITE_API_PROXY_TARGET`)
- [x] E2E failure root-cause validation and test hardening
- [x] Phase 3 evidence files refreshed under `.sisyphus/evidence/`
- [x] MCP API-key verification restored to DB-backed validation (removed permissive bypass)
- [x] Secret handling tightened in backend/MCP config and utility scripts (env-first placeholders)
- [x] Neo4j patent search query safety improvements (parameterization and relationship allowlist)
- [x] MCP schema contract alignment (`test_mcp_schemas.py` + endpoint compatibility)
- [x] Backend test baseline recovered to green (`50 passed`)

## Remaining environment tasks

- [ ] Install Firefox host dependency for Playwright (`libgtk-3-0`)
- [ ] Bring up MariaDB/Neo4j for full backend health (`/health/detailed` => `200`)
- [ ] Run full non-skip E2E after infrastructure is healthy
