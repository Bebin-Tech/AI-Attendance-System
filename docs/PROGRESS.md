# AIFAMS progress

## Phase 2 — database schema and migrations

Updated: 2026-11-07. **Implemented and verified locally on PostgreSQL 18.3 (the specification permits 16+). PostgreSQL 16 CI and full Compose execution remain unverified locally because the Docker engine is unavailable.**

### Files created or changed

- backend/app/models/schema.py: 56 UUID-based tables covering the full specified table list plus consent notices, batches, batch membership and events. Tenant indexes/composite foreign keys, status/date/range checks, unique attendance records, active-template/device constraints and same-person verification/consent links.
- backend/app/models/__init__.py and app/core/database.py: deferred/raiseload encrypted-template mapping and transaction-local tenant session helper. Config/environment examples split runtime and migration connections.
- backend/alembic.ini and migrations/: frozen 0001 schema revision and 0002 RLS/privilege/audit revision, async environment, offline SQL support and revision template. Migrations seed no domain records.
- backend/tests/: 7 metadata/schema tests and 25 real PostgreSQL tests, alongside the existing 4 health/API tests. Destructive migration fixtures require a new, empty aifams_test* database and never reset a non-empty database.
- backend/requirements.in and requirements.txt: Alembic 1.20.1 with pinned transitive dependencies; Dockerfile includes migration assets.
- infrastructure/docker/bootstrap-roles.sql and docker-compose.yml: separate runtime login and non-login service groups, idempotent local-role bootstrap, migration-before-API ordering. PostgreSQL image updated to 16.15.
- .github/workflows/ci.yml: real PostgreSQL 16 database service enables the integration tests; scripts/test.ps1 adds -RequireDatabase.
- docs/database/: compact ER diagrams, full 56-table Mermaid source and generated column/constraint/index dictionary. ADR 0003 documents tenant, privilege, audit and migration decisions. README and Windows installation instructions updated. scripts/export_schema_docs.py and the refusal-to-overwrite initial revision authoring helper are included.

### Commands and results

| Command / check | Result |
| --- | --- |
| uv pip compile / uv pip install | Alembic and required dependencies resolved and installed under Python 3.13.18. |
| python -m pytest -q (AIFAMS_TEST_DATABASE_URL set) | **36 passed**, zero skips, 1 upstream httpx TestClient deprecation warning; final run 12.82 seconds. |
| Alembic operations exercised by the integration fixture | Fresh upgrade head → check → downgrade 0001 → verify runtime column grants removed → upgrade head → downgrade base → assert no application tables → re-upgrade head → check. All passed; no metadata drift. |
| python -m ruff check . | Pass. |
| python -m ruff format --check . | Pass: 15 backend Python files. |
| python -m mypy app | Pass: 8 source files. |
| python -m pip_audit -r requirements.txt --no-deps --disable-pip | No known runtime dependency vulnerabilities. Pins are complete but not hash-locked; pip-audit warns accordingly. |
| python -m alembic upgrade head --sql | Pass: generated 56 application tables plus alembic_version, policies, privileges and triggers. |
| python scripts/export_schema_docs.py | Generated dictionary and full ER source for 56 tables. |
| docker compose -f infrastructure/docker-compose.yml config --quiet | Pass. Engine startup still fails with missing Docker Desktop Linux named pipe. |
| PowerShell AST check of scripts/test.ps1; git diff --check | Pass. |

The database tests prove missing-tenant denial; all 55 institution-root/tenant tables force RLS; cross-tenant reads/writes/FKs fail; tenant context clears after commit and rollback; API SQL cannot read encrypted template bytes or forge verification decisions; one active template per user/model; failed/mismatched verification cannot create present marks; manual marks require a reason; timestamps are server-set and immutable; 32 concurrent duplicate inserts create one record; 12 concurrent audit inserts form a valid, timezone-stable hash chain; audit UPDATE/DELETE/TRUNCATE fail even for the migration owner. These are database tests, not the Phase 8 1,000-request attendance API load test.

### Acceptance criteria

| Phase 2 criterion | Status | Evidence |
| --- | --- | --- |
| Fresh DB migrates up and down | Pass locally on PostgreSQL 18.3 | Both revisions reversed, empty-schema assertion, re-upgrade, and intermediate downgrade grant checks. |
| Schema tests pass | Pass | 36 backend tests, including 25 real database cases; strict types/lint clean. |
| ER diagram in docs | Pass | docs/database/README.md diagrams; complete schema.mmd and schema.md. |

### Known gaps and next step

1. Docker still cannot run locally. PostgreSQL 16 CI is configured but has not run for these local changes; no Docker build/Compose startup or GitHub CI success is claimed.
2. The official portable PostgreSQL 16 Windows initdb crashed with exit -1073740791. For local verification, official Ubuntu PostgreSQL 18.3 packages were installed in WSL, and a separate password-protected test cluster was started on loopback port 55432. Only disposable test databases were used; credentials/binaries/logs are in ignored .tools paths. This test server does not replace the Compose deployment.
3. Phase 2 does not implement user login, scoped RBAC, consent withdrawal/encryption services, calibrated face decisions, session eligibility, timetable clashes or attendance workflows. Those services must enforce current consent, session state, scope, thresholds and rate limits. RLS context must come from authenticated authorization in Phase 3.
4. Runtime table privileges are coarse service capabilities. Migration owners/superusers are privileged, and audit tamper evidence does not protect against a database administrator disabling triggers. Production must pre-provision least-privilege identities and manage secrets separately.
5. Phase 1's 10 moderate web development-tool advisories remain; the web source was unchanged in Phase 2. Runtime backend audit passes. The existing upstream TestClient deprecation is non-fatal.
6. Next: Phase 3 authentication, rotating refresh tokens, MFA, centralized authorization, audit-service integration and cross-tenant API policy tests.

## Phase 1 historical record

## Local browser recovery — 2026-11-07

The previous development URL timed out. Restarted native servers outside the restricted execution sandbox on web port 5180 and API port 8010. Opened and retained the actual app screen in the in-app browser. Verified the web server returns HTTP 200; the web proxy returns liveness HTTP 200 and readiness HTTP 503 because PostgreSQL/Redis are unavailable. Native Vite defaults now use fixed port 5180 and API 8010, with AIFAMS_API_TARGET override. Compose ports are unchanged. Native startup commands in README were updated. This recovers the screen and API connection; it does not satisfy Docker acceptance or add attendance functionality.

Updated: 2026-11-06. Scope: Phase 1 only. **Implemented; acceptance pending.**

## Files delivered

- Repository conventions, .gitignore, EditorConfig, pre-commit hooks, and Git initialization (no commit or remote).
- backend/: Python 3.13 FastAPI application, validated environment settings, dependency probes, consistent HTTP/validation errors and request IDs, pinned runtime dependency graph, Ruff/mypy/pytest configuration, four smoke tests, non-root multi-stage Dockerfile.
- web/: strict TypeScript React/Vite shell consuming actual readiness, dark/light styling, request timeout and cleanup, keyboard focus styles, npm lockfile, ESLint/Prettier/Vitest configuration, non-root Nginx Dockerfile and proxy.
- infrastructure/docker-compose.yml: PostgreSQL 16, Redis 7, API and web with dependency ordering, health checks, loopback ports and persistent PostgreSQL volume.
- .github/workflows/ci.yml: lint, formatting, types, tests, audits, production build, and Compose smoke job. No deploy or production secrets.
- scripts/: PowerShell setup, dev, test and explicitly gated destructive local database reset.
- docs/: architecture diagram, two ADRs, Windows instructions, supplied specification, this log, and npm audit evidence. Future service, Android and documentation directories are explicitly reserved.

## Commands and evidence

| Command | Observed result |
| --- | --- |
| uv python install 3.13 (project-local) | Python 3.13.18 installed; existing Python 3.14 was not used for application validation. |
| uv pip compile requirements.in / uv pip install | Runtime dependency graph pinned; runtime and development packages installed. |
| python -m ruff check . | Pass. |
| python -m ruff format --check . | Pass: 6 files already formatted. |
| python -m mypy app | Pass: 5 source files. |
| python -m pytest -q | Pass: 4 tests. One upstream httpx TestClient deprecation warning. |
| python -m pip_audit -r requirements.txt --no-deps --disable-pip | Pass: no known vulnerabilities found. Initial attempt timed out; retry succeeded. |
| npm install | Pass after clean sequential installation; all direct versions pinned and lockfile generated. |
| npm run lint / format:check / test / build | Pass: lint zero warnings; source formatting clean; Vitest exits 0 with no tests; TypeScript and Vite build succeed (16 modules). Generated dist is excluded from source formatting. No component or E2E coverage is claimed. |
| PowerShell AST parse of scripts/*.ps1 | Pass: all 4 scripts. |
| docker compose -f infrastructure/docker-compose.yml config --quiet | Pass. |
| docker compose -f infrastructure/docker-compose.yml up --build --wait --wait-timeout 60 | Blocked: Docker Desktop Linux engine named pipe missing. No container build/start success claimed. |

Sandbox restrictions stalled the first pytest invocation; the approved execution passed. Early npm pins had advisories and an unsupported ESLint version; maintained versions were selected. An overlapping npm repair caused generated-folder conflicts; both processes exited, then a single clean installation succeeded.

## Acceptance criteria

| Phase 1 criterion | Status | Evidence |
| --- | --- | --- |
| Repo, structure, tooling, architecture and ADRs | Pass | Files above. |
| docker compose up starts all services | Not passed | Configuration validates; Docker engine unavailable. |
| CI runs lint and empty tests | Pending remote execution | Workflow exists; local quality checks recorded above. GitHub CI has not run. |

## Known gaps and next step

1. Start/repair Docker Desktop's Linux engine, rerun Compose and HTTP smoke checks, then mark Phase 1 accepted only after success. PowerShell troubleshooting is in installation/windows.md.
2. npm audit reports 10 moderate advisories in the development lint dependency graph (minimatch amplification and dependent packages); no high/critical advisories remain. Full evidence is web-audit.json. Do not force incompatible dependency downgrades/overrides. Audit cleanliness remains unresolved; CI currently enforces the high threshold and reports moderate findings.
3. Browser visual QA, Lighthouse, accessibility audit, E2E and Android tests have not run. These are not claimed complete. The React review checked component boundaries, effect cleanup, functional updates, semantics, strict types, and minimal dependencies.
4. Images use version tags rather than immutable digests. Native platform differences mean the Linux Docker wheel build must still be verified. Python dev tools are directly pinned; full development transitive hashing remains future supply-chain work.
5. No database schema/migrations, auth, domain data, workers, face models, production profile, TLS, monitoring or mobile implementation is included in this phase. No ML licence/compatibility conclusions are implied; ADR 0002 defines the later selection gate.
6. Next implementation phase after foundation acceptance: schema, tenant constraints, indexes, Alembic up/down verification and ER diagram (Phase 2).
