# ADR-006: CORS Security Hardening Approach

**Date**: 2025-12-31
**Status**: Accepted
**Decider**: Claude Code (AI-First Development)

## Context

The TaskFlow backend is served from Railway, while the frontend is hosted on Vercel. Cross-Origin Resource Sharing (CORS) must be configured to allow legitimate frontend requests while blocking unauthorized origins.

## Decision

Implement strict CORS whitelist with the following approach:

1. **Whitelist-only approach**: Only explicitly configured origins are allowed
2. **No wildcards**: No `*` allowed, even in development
3. **Production-only Vercel domains**: Only production frontend URLs allowed in production
4. **No automatic localhost**: Development mode must explicitly configure localhost

## Implementation

```python
# In main.py
def get_cors_origins() -> list[str]:
    origins = settings.get_cors_origins_list()

    if is_production:
        # Strict: Only configured Vercel origins
        return origins
    else:
        # Development: Allow configured + localhost
        if "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
        return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rationale

1. **Security First**: Explicit whitelisting prevents accidental exposure
2. **Predictable**: Clear list of allowed origins in configuration
3. **Fail-Safe**: Unconfigured origins are automatically denied
4. **Production Safe**: No localhost automatically added in production

## Alternatives Considered

1. **Dynamic CORS based on request**: Rejected - complex, potential for bypass
2. **Regex-based origin matching**: Rejected - harder to audit, potential for regex exploits
3. **Environment-specific origin lists**: Accepted - explicit configuration per environment

## Consequences

### Positive
- Strong security posture
- Clear audit trail of allowed origins
- Prevents domain hijacking

### Negative
- Requires explicit configuration for each deployment
- Must update CORS_ORIGINS when adding new frontend domains

## Configuration

| Environment | Allowed Origins |
|-------------|-----------------|
| Production | Vercel production URLs (from `CORS_ORIGINS` env var) |
| Development | Configured origins + localhost:3000 |

**Reference**: `backend/src/main.py:39-55`
