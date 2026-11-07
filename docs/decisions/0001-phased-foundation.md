# ADR 0001: Deliver a runnable foundation before domain features

Status: accepted. Date: 2026-11-06.

The supplied operating contract requires sequential phases. Phase 1 contains FastAPI health probes, a React operational shell, Compose, CI, tooling and documentation. No fake business features or statistics are exposed. Schema and Alembic begin in Phase 2; authentication and central authorization begin in Phase 3. Android builds begin in Phase 10. Empty package directories describe future boundaries, not implemented services.

Use Python 3.13, Node 24 LTS, PostgreSQL 16 and Redis 7. API and static-web images run as non-root. Only loopback development ports are published. Native Python 3.14 is not a substitute for the required runtime. Runtime Python dependencies are resolved into requirements.txt from requirements.in; npm's full dependency graph is locked. Image digest pinning remains supply-chain work and is not claimed complete.

Sources: [FastAPI container guidance](https://fastapi.tiangolo.com/deployment/docker/), [Vite Node requirements](https://vite.dev/guide/).
