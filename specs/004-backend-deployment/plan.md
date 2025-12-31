# Implementation Plan: Backend Production Deployment

**Branch**: `004-backend-deployment` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-backend-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Configure FastAPI backend for production deployment on Railway with:
1. Dynamic port binding via `PORT` environment variable and root-level `Procfile`
2. Optimized asyncpg connection pooling for Neon serverless PostgreSQL
3. CORS hardening to whitelist Vercel production domains only
4. Secret externalization (no hardcoded fallbacks for production secrets)
5. Deep health check endpoint for database connectivity verification
6. Production verification test suite for live environment validation

## Technical Context

**Language/Version**: Python 3.13+ (existing `.python-version`)
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22, asyncpg 0.30+, uvicorn 0.30+
**Storage**: Neon PostgreSQL (serverless, asyncpg driver)
**Testing**: pytest (to be configured), production verification scripts
**Target Platform**: Railway (Linux container)
**Project Type**: web (FastAPI backend)
**Performance Goals**: Sub-10ms cold start, connection pool of 5-10 for serverless
**Constraints**: Dynamic port binding ($PORT), strict CORS, no hardcoded secrets
**Scale/Scope**: Single-instance production deployment, up to 100 concurrent connections

### Deployment Configuration Details

| Component | Value | Source |
|-----------|-------|--------|
| Port | `$PORT` (dynamic) | Railway environment variable |
| Host | `0.0.0.0` | Railway requirement |
| Database Protocol | `postgresql+asyncpg://` | Neon optimized |
| Pool Size | 5-10 connections | Serverless autoscaling |
| Pool Mode | transaction | Neon PgBouncer default |
| CORS | Vercel domains only | Production security |

### Research Findings (from Context7 + Neon Docs)

1. **Railway Procfile**: `web: uvicorn src.main:app --host 0.0.0.0 --port $PORT`
2. **Neon Pooling**: Use `-pooler` suffix in hostname for transaction pooling
3. **Connection Limits**: `max_connections = max(100, min(4000, 450.5 * compute_size))`
4. **Serverless Config**: `pool_size=5-10`, `max_overflow=2` for asyncpg in serverless

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Spec-Driven Development | ✅ PASS | `spec.md` exists and defines all requirements |
| II. AI-First Development | ✅ PASS | Planning via `/sp.plan` workflow |
| III. Test-First (TDD) | ⚠️ TODO | Verification tests to be written in `/sp.tasks` |
| IV. Free-Tier First | ✅ PASS | Railway free tier + Neon free tier |
| V. Progressive Architecture | ✅ PASS | Builds on existing Phase II backend |
| VI. Stateless & Cloud-Native | ✅ PASS | JWT auth, database-backed state |
| VII. Simplicity & YAGNI | ✅ PASS | Only required production configs |

### Gate Evaluation

- ✅ All functional requirements are in `spec.md`
- ✅ No code implementation without specification
- ✅ Free-tier services confirmed (Railway + Neon)
- ⚠️ Tests will be created in `/sp.tasks` phase (not yet)

## Project Structure

### Documentation (this feature)

```text
specs/004-backend-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (inline above)
├── data-model.md        # Phase 1 output (not applicable - no data model changes)
├── quickstart.md        # Phase 1 output (deployment quickstart)
├── contracts/           # Phase 1 output (API health check spec)
│   └── health-check.yaml
├── verify-production/   # Phase 2 output (verification scripts)
│   └── test_suite.py
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── Procfile                    # NEW: Railway process definition
├── src/
│   ├── main.py                 # MODIFY: Port binding, CORS, docs disabled
│   ├── config.py               # MODIFY: Secret externalization, production detection
│   ├── database.py             # MODIFY: Connection pool optimization
│   └── middleware.py           # EXISTING: Rate limiting
├── verify_production.py        # NEW: Production verification script
└── pyproject.toml              # MODIFY: Add production dependencies if needed
```

**Structure Decision**: All configuration files are added to `backend/` directory since this is a backend-only deployment feature.

## Complexity Tracking

> No complexity violations. This feature adds production configuration without architectural changes.

## Phase 0: Research Summary

### Decisions Resolved

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Port Binding | `$PORT` env var | Railway provides dynamic port via env |
| Pool Size | 5-10 connections | Balances Neon free tier limits with concurrency |
| CORS | Domain whitelist | Security hardening for production |
| Health Check | Real DB query | Deep health verification, not just ping |
| Docs in Prod | Disabled | Security best practice unless explicitly enabled |

### Alternatives Considered

1. **Connection Pooling**: Considered PgBouncer sidecar → Rejected (over-engineering for free tier)
2. **CORS Regex**: Considered dynamic CORS → Rejected (whitelist is more secure)
3. **Health Check**: Considered `/livez` + `/readyz` → Accepted as `/health` with db check

## Phase 1: Design Artifacts

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `backend/Procfile` | CREATE | Railway process definition |
| `backend/verify_production.py` | CREATE | Production verification suite |
| `backend/src/config.py` | MODIFY | Secret externalization, env detection |
| `backend/src/main.py` | MODIFY | CORS hardening, docs disabled, port binding |
| `backend/src/database.py` | MODIFY | Pool optimization for Neon |
| `specs/004-backend-deployment/contracts/health-check.yaml` | CREATE | OpenAPI health check spec |
| `specs/004-backend-deployment/quickstart.md` | CREATE | Deployment instructions |

### API Contract: Health Check Endpoint

```yaml
/openapi.yaml:
  /health:
    get:
      summary: Deep Health Check
      description: Verifies database connectivity and returns system status
      responses:
        '200':
          description: System healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [ok, unhealthy]
                  database:
                    type: string
                    enum: [connected, disconnected]
                  environment:
                    type: string
                    enum: [production, development]
                  timestamp:
                    type: string
                    format: date-time
        '503':
          description: Database unavailable
```

### Connection Pool Configuration

```python
# backend/src/database.py additions
from sqlalchemy.pool import NullPool

# For production: use limited pool
engine = create_async_engine(
    database_url,
    pool_size=10,           # Neon recommended for serverless
    max_overflow=2,         # Burst capacity
    pool_pre_ping=True,     # Verify connections
    pool_recycle=3600,      # Recycle connections hourly
    echo=False,
)
```

## Phase 2: Implementation Tasks

> Generated by `/sp.tasks` command

Tasks will include:
1. Create `Procfile` for Railway
2. Update `config.py` for secret externalization
3. Configure CORS for Vercel whitelist
4. Implement deep health check with DB query
5. Optimize asyncpg connection pooling for Neon
6. Create `verify_production.py` verification suite
7. Write ADR for each architectural decision

---

## Output Artifacts

| Artifact | Path |
|----------|------|
| Implementation Plan | `specs/004-backend-deployment/plan.md` |
| Research Summary | Inline in plan.md (Phase 0) |
| Quickstart | `specs/004-backend-deployment/quickstart.md` |
| Health Contract | `specs/004-backend-deployment/contracts/health-check.yaml` |
| Tasks | `specs/004-backend-deployment/tasks.md` (via `/sp.tasks`) |
| ADRs | `history/adr/` (via `/sp.adr`) |

**Branch**: `004-backend-deployment`
**Plan Path**: `/home/ruser/q4/todo-app-web/specs/004-backend-deployment/plan.md`
**Next Step**: Run `/sp.tasks` to generate implementation tasks
