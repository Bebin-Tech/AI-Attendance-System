# AIFAMS progress

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
