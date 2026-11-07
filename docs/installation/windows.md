# Windows setup and troubleshooting

Use PowerShell on Windows 10/11. Install Python 3.13 (ensure `py -3.13 --version` works), Node 24 LTS, Git, and Docker Desktop using Linux containers. Start Docker Desktop and wait until `docker info` prints server information.

Run the commands in README. Setup should finish with successful pip installation and npm's dependency summary; test should print pytest totals and a Vite build. The Compose `--wait` command should exit successfully only after all services become healthy. Swagger is at `/api/v1/docs`, not `/docs`.

Common problems:

| Symptom | Action |
| --- | --- |
| Docker named pipe missing | Start Docker Desktop; confirm Linux containers and WSL2 prerequisites; rerun `docker info`. |
| `py` opens Store or cannot launch | Install Python 3.13 and fix Windows app execution aliases. Set `AIFAMS_PYTHON` to the full Python 3.13 executable path for setup.ps1. |
| npm.ps1 blocked | Use `npm.cmd` or run Node with npm's npm-cli.js entrypoint; do not disable machine-wide policy. |
| DNS ENOTFOUND / pip name resolution error | Check proxy/DNS/network permissions; no dependency compatibility conclusion follows from a network failure. |
| Port 5432/6379/8000/8080 in use | Stop the conflicting development process or change the Compose published port and native environment accordingly. |
| API ready returns 503 | Check `docker compose -f infrastructure/docker-compose.yml logs postgres redis api`. Confirm database/cache URLs; never paste secrets into bug reports. |
| Web dependencies missing | Run setup or `npm ci` in web; npm ci requires the committed lockfile. |

`reset-db.ps1` is destructive and requires the explicit `-ConfirmReset` switch. It removes this Compose project's named database volume. Never use it against institutional data.

Phase 2 adds Alembic migrations and separate migration/runtime database identities. Follow the [database guide](../database/README.md) to provision roles, apply revisions and run disposable-database tests. Native development uses web port 5180 and API port 8010; Compose uses 8080 and 8000. Android SDK/emulator setup and production operations will be documented in their implementation phases.
