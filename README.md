# AIFAMS

AI Face Attendance Management System for colleges. Work proceeds through the 15 phases in the supplied specification. **Phase 1 foundation only: no authentication, attendance processing, or biometric enrollment is available. Not ready for institutional deployment.**

## Start on Windows

Prerequisites: Docker Desktop with its Linux engine running. For native development: Python **3.13**, Node **24 LTS**, and Git. All commands below use PowerShell from this directory.

```powershell
docker compose -f infrastructure/docker-compose.yml up --build --wait
```

Expected: four running services, all healthy. Open [web](http://localhost:8080), [Swagger](http://localhost:8000/api/v1/docs), [liveness](http://localhost:8000/api/v1/health/live), and [readiness](http://localhost:8000/api/v1/health/ready). The web readiness message is fetched from the API; it contains no sample attendance data.

```powershell
.\scripts\setup.ps1
.\scripts\test.ps1
.\scripts\dev.ps1
```

`setup.ps1` creates backend/.venv, installs dependencies, and copies the environment example without overwriting an existing .env. `test.ps1` runs Python lint, format, types, tests and web lint, format, tests, and build. `dev.ps1` runs Compose in the foreground. Stop with Ctrl+C, then `docker compose -f infrastructure/docker-compose.yml down`. Database volumes persist.

For separate terminals after setup:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8010
```

```powershell
Set-Location web
npm run dev
```

Native web development opens at http://127.0.0.1:5180 and proxies the API to port 8010. Compose continues to use web port 8080 and API port 8000. Set AIFAMS_API_TARGET before starting Vite to override the native API destination.

Native API readiness requires Postgres and Redis: `docker compose -f infrastructure/docker-compose.yml up -d postgres redis`.

See [installation](docs/installation/windows.md), [architecture](docs/architecture/overview.md), [decisions](docs/decisions/0001-phased-foundation.md), and [progress and validation](docs/PROGRESS.md).

## Scope and safety

Compose credentials are local development defaults; ports bind to loopback. There are no user accounts, templates, seeds, or attendance records. Do not expose this configuration to the internet. Production TLS, secret management, tenant policies, jobs, metrics, Android, privacy workflows, and model evaluation belong to later phases. Migrations start in Phase 2; no schema is created on application startup.

GitHub Actions runs foundation checks and a Compose integration smoke test. Android and service directories reserve structure only, with no claimed implementations. CI execution on GitHub is not implied by local checks.
