# ADR-004: Railway Port Binding Strategy

**Date**: 2025-12-31
**Status**: Accepted
**Decider**: Claude Code (AI-First Development)

## Context

The TaskFlow backend needs to be deployed on Railway, which provides dynamic port assignment via the `PORT` environment variable. The application must bind to this port for external accessibility.

## Decision

Use `uvicorn` with dynamic port binding via `$PORT` environment variable in a Railway `Procfile`:

```Procfile
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
```

## Rationale

1. **Railway Standard**: Railway sets `PORT` environment variable for each deployed service
2. **uvicorn Compatibility**: uvicorn natively supports `--port $PORT` syntax
3. **Simplicity**: No custom startup script required
4. **Host Binding**: `0.0.0.0` required for Railway's reverse proxy to reach the app
5. **Workers**: Single worker recommended for serverless/free tier (avoids memory issues)

## Alternatives Considered

1. **Custom startup script**: Rejected - unnecessary complexity for simple port binding
2. **gunicorn with uvicorn workers**: Rejected - gunicorn adds overhead, single uvicorn sufficient for free tier
3. **Environment variable detection in Python**: Rejected - uvicorn handles this natively

## Consequences

### Positive
- Simple, maintainable deployment configuration
- No custom code required for port binding
- Follows Railway best practices

### Negative
- None significant for free tier deployment

## Implementation

The Procfile is placed at `backend/Procfile` (monorepo structure) and uvicorn command runs from the `backend/` directory.

**Reference**: `backend/Procfile:1`
